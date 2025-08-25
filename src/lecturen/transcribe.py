from pathlib import Path
from typing import List, Tuple
from faster_whisper import WhisperModel
from .models import TranscriptSegment, Transcript
from .utils.io import write_json
from .utils.timestamps import seconds_to_timestamp

def transcribe_audio(audio_path: Path, model_size: str = "small") -> Transcript:
    model = WhisperModel(model_size, device="auto", compute_type="int8")
    segments, info = model.transcribe(str(audio_path), beam_size=5)
    out_segments: List[TranscriptSegment] = []
    language = info.language if hasattr(info, "language") else None
    for seg in segments:
        out_segments.append(
            TranscriptSegment(start=seg.start, end=seg.end, text=seg.text, language=language)
        )
    return Transcript(segments=out_segments, language=language)

def write_srt(transcript: Transcript, srt_path: Path) -> None:
    lines = []
    for idx, seg in enumerate(transcript.segments, start=1):
        start_ms = int(seg.start * 1000)
        end_ms = int(seg.end * 1000)
        start = f"{start_ms//3600000:02d}:{(start_ms//60000)%60:02d}:{(start_ms//1000)%60:02d},{start_ms%1000:03d}"
        end = f"{end_ms//3600000:02d}:{(end_ms//60000)%60:02d}:{(end_ms//1000)%60:02d},{end_ms%1000:03d}"
        lines.append(str(idx))
        lines.append(f"{start} --> {end}")
        lines.append(seg.text.strip())
        lines.append("")
    srt_path.parent.mkdir(parents=True, exist_ok=True)
    srt_path.write_text("\n".join(lines), encoding="utf-8")

def persist_transcript(transcript: Transcript, json_path: Path, srt_path: Path) -> None:
    write_json(json_path, transcript.model_dump())
    write_srt(transcript, srt_path)
