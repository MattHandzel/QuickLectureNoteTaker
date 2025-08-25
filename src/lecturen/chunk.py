from __future__ import annotations
from typing import List, Dict, Any
from .models import Transcript, TranscriptSegment
from .utils.timestamps import seconds_to_timestamp

def chunk_transcript(transcript: Transcript, max_chars: int = 4000, overlap_seconds: int = 8) -> List[Dict[str, Any]]:
    chunks: List[Dict[str, Any]] = []
    current: List[TranscriptSegment] = []
    current_len = 0
    def add_chunk(segments: List[TranscriptSegment]):
        if not segments:
            return
        text = " ".join(s.text.strip() for s in segments if s.text.strip())
        start = segments[0].start
        end = segments[-1].end
        chunks.append({
            "text": text,
            "start": start,
            "end": end,
            "start_ts": seconds_to_timestamp(start),
            "end_ts": seconds_to_timestamp(end),
            "segments": [s.model_dump() for s in segments],
        })
    for seg in transcript.segments:
        seg_text = seg.text.strip()
        if not seg_text:
            continue
        if current_len + len(seg_text) + 1 > max_chars and current:
            add_chunk(current)
            tail: List[TranscriptSegment] = []
            tail_start = seg.start - overlap_seconds
            for s in reversed(current):
                if s.start >= tail_start:
                    tail.insert(0, s)
                else:
                    break
            current = tail
            current_len = sum(len(s.text) for s in current)
        current.append(seg)
        current_len += len(seg_text) + 1
    if current:
        add_chunk(current)
    return chunks
