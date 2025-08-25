import sys
from pathlib import Path
import json
import typer
import logging
from .utils.logging import setup_logging
from .config import load_config, save_config
from .ingest import prepare_workspace
from .audio import extract_wav_mono_16k
from .transcribe import transcribe_audio, persist_transcript

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
    typer.echo("Render not implemented yet")

if __name__ == "__main__":
    app()
