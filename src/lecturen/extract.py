from __future__ import annotations
from typing import List, Dict, Any
import os
import json
from tenacity import retry, stop_after_attempt, wait_exponential
from .models import AtomicNote, NoteType
from .utils.io import write_json

def _build_prompt(template: str, chunk: Dict[str, Any]) -> str:
    return template.format(
        chunk_text=chunk["text"],
        start_ts=chunk["start_ts"],
        end_ts=chunk["end_ts"],
    )

def _parse_items(raw: str) -> List[AtomicNote]:
    data = json.loads(raw)
    if not isinstance(data, list):
        raise ValueError("Expected a list JSON")
    items: List[AtomicNote] = []
    for obj in data:
        if "type" in obj and obj["type"] in [t.value for t in NoteType]:
            pass
        else:
            raise ValueError("Invalid type")
        items.append(AtomicNote(
            type=NoteType(obj["type"]),
            title=obj.get("title","").strip(),
            body=obj.get("body","").strip(),
            timestamp=obj.get("timestamp","00:00"),
            span=obj.get("span", ["00:00","00:00"]),
            importance=int(obj.get("importance",1)),
            tags=list(obj.get("tags", [])),
            image_path=obj.get("image_path"),
        ))
    return items

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=8))
def _call_openai(prompt: str, model: str = "gpt-4o-mini") -> str:
    from openai import OpenAI
    client = OpenAI()
    resp = client.chat.completions.create(
        model=model,
        messages=[
            {"role":"system","content":"Output STRICT JSON only. No prose or comments."},
            {"role":"user","content":prompt},
        ],
        temperature=0.2,
        max_tokens=1200,
    )
    content = resp.choices[0].message.content
    if not content:
        raise RuntimeError("Empty response")
    return content

def extract_items_for_chunks(chunks: List[Dict[str, Any]], template_text: str, out_dir) -> List[AtomicNote]:
    use_openai = bool(os.environ.get("OPENAI_API_KEY"))
    if not use_openai:
        raise RuntimeError("OPENAI_API_KEY not set. Enable cloud extraction or implement local model.")
    all_items: List[AtomicNote] = []
    for idx, ch in enumerate(chunks):
        prompt = _build_prompt(template_text, ch)
        raw = _call_openai(prompt)
        items = _parse_items(raw)
        write_json(out_dir / f"chunk_{idx:03d}.json", [i.model_dump() for i in items])
        all_items.extend(items)
    return all_items
