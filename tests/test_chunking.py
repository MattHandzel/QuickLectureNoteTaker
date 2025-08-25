from pathlib import Path
import orjson
from lecturen.models import Transcript
from lecturen.chunk import chunk_transcript

def test_chunking_simple():
    data = orjson.loads(Path("tests/fixtures/sample_transcript.json").read_bytes())
    tr = Transcript(**data)
    chunks = chunk_transcript(tr, max_chars=80, overlap_seconds=3)
    assert len(chunks) >= 1
    for ch in chunks:
        assert "text" in ch and ch["text"]
        assert ch["start"] <= ch["end"]
        assert "start_ts" in ch and "end_ts" in ch
