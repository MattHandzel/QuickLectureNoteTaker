from __future__ import annotations
from typing import List, Dict, Any
from pathlib import Path
from datetime import datetime
from .models import AtomicNote, Transcript
from .utils.io import write_text

SECTION_ORDER = ["Definition","Concept","Theorem","Procedure","Example","Equation","Pitfall","QA"]

def _front_matter(meta: Dict[str, Any]) -> str:
    lines = ["---"]
    for k, v in meta.items():
        if isinstance(v, list):
            list_str = "[" + ", ".join(str(x) for x in v) + "]"
            lines.append(f"{k}: {list_str}")
        elif isinstance(v, str):
            lines.append(f'{k}: "{v}"')
        else:
            lines.append(f"{k}: {v}")
    lines.append("---")
    return "\n".join(lines)

def _render_section(title: str, items: List[AtomicNote]) -> str:
    if not items:
        return ""
    out = [f"## {title}"]
    for it in items:
        out.append(f"- [{it.timestamp}] {it.title} (importance: {it.importance})")
        body = it.body.strip()
        if body:
            out.append(f"  \n  {body}")
    return "\n".join(out)

def _render_transcript(transcript: Transcript) -> str:
    lines = ["<details>", "<summary>Transcript</summary>", ""]
    for seg in transcript.segments:
        lines.append(f"- [{int(seg.start//60):02d}:{int(seg.start%60):02d}] {seg.text.strip()}")
    lines.append("</details>")
    return "\n".join(lines)

def render_markdown(title: str, source: str, transcript_model: str, llm_model: str, duration: str, items: List[AtomicNote], transcript: Transcript) -> str:
    meta = {
        "title": title,
        "source": source,
        "created": datetime.utcnow().isoformat(),
        "duration": duration,
        "transcript_model": transcript_model,
        "llm_model": llm_model,
        "tags": ["lecture"],
    }
    sections = []
    for sec in SECTION_ORDER:
        sec_items = [i for i in items if i.type.value == sec]
        sections.append(_render_section(sec, sec_items))
    sections = [s for s in sections if s]

    out_lines = []
    out_lines.append(_front_matter(meta))
    out_lines.append(f"# {title}")
    if sections:
        out_lines.append("")
        sections_block = "\n\n".join(sections)
        out_lines.append(sections_block)
    out_lines.append("## Links")
    out_lines.append("")
    out_lines.append(_render_transcript(transcript))
    return "\n".join(out_lines)

def write_markdown(path: Path, text: str) -> None:
    write_text(path, text)
