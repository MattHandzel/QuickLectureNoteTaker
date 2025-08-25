from pathlib import Path
from lecturen.models import AtomicNote, NoteType, Transcript, TranscriptSegment
from lecturen.render import render_markdown

def norm_dynamic(text: str) -> str:
    lines = []
    for ln in text.splitlines():
        if ln.startswith("created: "):
            lines.append('created: "IGNORE"')
        else:
            lines.append(ln)
    return "\n".join(lines).strip()

def test_render_golden(tmp_path: Path):
    segments = [
        TranscriptSegment(start=0, end=5, text="Definition: A graph is a pair (V, E)."),
        TranscriptSegment(start=5, end=12, text="Example: Consider a graph with vertices 1,2,3 and edges (1,2)."),
        TranscriptSegment(start=12, end=20, text="Procedure: To add an edge, first ensure vertices exist, then insert the pair."),
    ]
    transcript = Transcript(segments=segments, language="en")
    items = [
        AtomicNote(type=NoteType.Definition, title="Graph", body="A graph is a pair (V, E).", timestamp="00:00", span=["00:00","00:05"]),
        AtomicNote(type=NoteType.Example, title="Example graph", body="Consider a graph with vertices 1,2,3 and edges (1,2).", timestamp="00:05", span=["00:05","00:12"]),
        AtomicNote(type=NoteType.Procedure, title="Add an edge", body="To add an edge, first ensure vertices exist, then insert the pair.", timestamp="00:12", span=["00:12","00:20"]),
    ]
    md = render_markdown("Sample", "sample.mp4", "fw", "dummy", "", items, transcript)
    expected = Path("tests/golden/render_simple.md").read_text(encoding="utf-8").strip()
    assert norm_dynamic(md) == expected
