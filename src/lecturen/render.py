from __future__ import annotations
from typing import List, Dict
from pathlib import Path
from datetime import datetime
from .models import AtomicNote, Transcript
from .utils.io import write_text

SECTION_ORDER = ["Definition","Concept","Theorem","Procedure","Example","Equation","Pitfall","QA"]

def _front_matter(meta: Dict[str,str]) -> str:
    lines = ["---"]
    for k,v in meta.items():
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
    out.append("")
    return "\n".join(out)

def _render_transcript(transcript: Transcript) -> str:
    lines = ["<details>", "<summary>Transcript</summary>", ""]
    for seg in transcript.segments:
        lines.append(f"- [{int(seg.start//60):02d}:{int(seg.start%60):02d}] {seg.text.strip()}")
    lines.append("</details>")
    return "\n".join(lines)

def render_markdown(title: str, source: str, transcript_model: str, llm_model: str, duration: str, items: List[AtomicNote], transcript: Transcript) -> str:
    meta = {
        "title": f"\"{title}\"",
        "source": f"\"{source}\"",
        "created": f"\"{datetime.utcnow().isoformat()}\"",
        "duration": f"\"{duration}\"",
        "transcript_model": f"\"{transcript_model}\"",
        "llm_model": f"\"{llm_model}\"",
        "tags": "[lecture]",
    }
    sections = []
    for sec in SECTION_ORDER:
        sec_items = [i for i in items if i.type.value == sec]
        sections.append(_render_section(sec, sec_items))
    sections = [s for s in sections if s]
    parts = [
        _front_matter(meta),
        f"# {title}",
        "\n".join(sections),
        "## Links\n",
        _render_transcript(transcript),
    ]
    return "\n\n".join(parts)

def write_markdown(path: Path, text: str) -> None:
    write_text(path, text)
