import sys
from pathlib import Path
import json
import typer
import logging
import os
from .utils.logging import setup_logging
from .config import load_config, save_config
from .ingest import prepare_workspace
from .audio import extract_wav_mono_16k
from .transcribe import transcribe_audio, persist_transcript
from .chunk import chunk_transcript
from .extract import extract_items_for_chunks
from .normalize import dedupe_and_merge
from .render import render_markdown, write_markdown
from .utils.io import read_json, write_json

app = typer.Typer(add_completion=False)

@app.callback()
def main(
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose logging"),
):
    setup_logging("DEBUG" if verbose else "INFO")

@app.command()
def ingest(
    video_or_url: str = typer.Argument(..., help="Path to local video file or a URL"),
    title: str = typer.Option(None, "--title", help="Optional lecture title override"),
    asr: str = typer.Option("local", "--asr", help="ASR mode: local or openai"),
    extract: bool = typer.Option(True, "--extract/--no-extract", help="Run extraction and draft render"),
    repo_root: str = typer.Option(".", "--repo-root", help="Repository root for workspace"),
):
    cfg = load_config()
    root = Path(repo_root).resolve()
    workspace, meta = prepare_workspace(video_or_url, root)
    logging.info(f"Session: {meta.session_id}")
    source_path = Path(meta.source)
    audio_path = workspace / "audio" / "audio.wav"
    extract_wav_mono_16k(source_path, audio_path)
    tr = transcribe_audio(audio_path, model_size="small")
    meta.transcript_model = "faster-whisper:small-int8"
    json_path = workspace / "transcript" / "transcript.json"
    srt_path = workspace / "transcript" / "transcript.srt"
    persist_transcript(tr, json_path, srt_path)
    meta_path = workspace / "meta.json"
    meta_path.write_text(json.dumps(meta.model_dump(), indent=2, default=str), encoding="utf-8")
    logging.info(f"Transcript written to {json_path}")
    logging.info(f"SRT written to {srt_path}")

    if extract:
        from .models import Transcript
        transcript = Transcript(**read_json(json_path))
        chunks = chunk_transcript(transcript, max_chars=cfg.get("chunk_chars", 4000), overlap_seconds=cfg.get("overlap_seconds", 8))
        (workspace / "extraction").mkdir(parents=True, exist_ok=True)
        prompt_path = Path(__file__).resolve().parent / "prompts" / "extraction_prompt.txt"
        template = prompt_path.read_text(encoding="utf-8")
        try:
            items = extract_items_for_chunks(chunks, template, workspace / "extraction")
            merged = dedupe_and_merge(items)
            write_json(workspace / "extraction" / "items.json", [i.model_dump() for i in merged])
            draft = render_markdown(
                title or Path(meta.source).stem,
                meta.source,
                meta.transcript_model or "",
                "openai",
                "",
                merged,
                transcript,
            )
            write_markdown(workspace / "draft.md", draft)
            logging.info(f"Draft written to {workspace / 'draft.md'}")
        except Exception as e:
            logging.error(f"Extraction failed: {e}")

    logging.info(f"Session ID: {meta.session_id}")
    typer.echo(meta.session_id)

@app.command()
def review(
    session_id: str = typer.Argument(..., help="Session ID to review"),
    repo_root: str = typer.Option(".", "--repo-root", help="Repository root"),
):
    typer.echo("Review TUI not implemented yet")

@app.command()
def render(
    session_id: str = typer.Argument(..., help="Session ID to render"),
    vault_path: str = typer.Option(None, "--vault-path", help="Override vault path"),
    subfolder: str = typer.Option(None, "--subfolder", help="Vault subfolder"),
    repo_root: str = typer.Option(".", "--repo-root", help="Repository root"),
):
    root = Path(repo_root).resolve()
    session_dir = root / ".lecturen" / "sessions" / session_id
    items_path = session_dir / "extraction" / "items.json"
    json_path = session_dir / "transcript" / "transcript.json"
    meta_path = session_dir / "meta.json"
    if not items_path.exists() or not json_path.exists():
        typer.echo("Missing items or transcript. Run ingest with extraction first.", err=True)
        raise typer.Exit(1)
    from .models import Transcript, AtomicNote
    items = [AtomicNote(**x) for x in read_json(items_path)]
    transcript = Transcript(**read_json(json_path))
    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    md = render_markdown(
        Path(meta["source"]).stem,
        meta["source"],
        meta.get("transcript_model",""),
        meta.get("llm_model",""),
        "",
        items,
        transcript,
    )
    out_path = session_dir / "final.md"
    write_markdown(out_path, md)
    typer.echo(str(out_path))

if __name__ == "__main__":
    app()
