# QuickLectureNoteTaker

Automates information capture from lecture videos by extracting audio, transcribing the content, and producing exhaustive, atomic, timestamped notes grouped by type, ready for review and export to an Obsidian vault.

## Status

M1 implements ingest → audio extract → transcription with a CLI. Subsequent milestones will add chunking, schema-constrained extraction, normalization, Markdown rendering, and a review TUI.

## Installation

Option A: Nix (recommended)

- Install Nix with flakes enabled.
- Enter the dev shell:

```
nix develop
```

Option B: Python venv

```
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

System dependencies

- ffmpeg
- yt-dlp

On Nix these are provided by the dev shell.

## CLI

After installing (pyproject exposes `lecturen`):

```
lecturen --help
```

### Ingest

```
lecturen ingest ./example_lecture.mp4
```

This creates a workspace under `.lecturen/sessions/<session_id>/` with:

- `source/` original media
- `audio/audio.wav` mono 16 kHz wav
- `transcript/transcript.json` segments with timestamps
- `transcript/transcript.srt` subtitle file
- `meta.json` session metadata

It prints the `session_id` for follow-up commands.

### Review and Render

Placeholders for now:

```
lecturen review <session_id>
lecturen render <session_id> [--vault-path ...] [--subfolder capture]
```

### Extraction and Render (M2)

Local-first: cloud extraction is opt-in. Set `OPENAI_API_KEY` to enable extraction using OpenAI.

Example:
```
export OPENAI_API_KEY=sk-...
lecturen ingest ./example_lecture.mp4 --extract
# A draft is written to .lecturen/sessions/<id>/draft.md
```

To render (re-run later):
```
lecturen render <session_id>
# Writes .lecturen/sessions/<id>/final.md
```

Notes:
- Only transcript chunks are sent to the API; raw video is never uploaded.
- If `OPENAI_API_KEY` is not set or `--no-extract` is used, the pipeline stops after transcription.

These will be implemented in M3/M2 respectively.

## Configuration

Environment variables and user config are supported:

- `LECTUREN_VAULT_PATH` default vault path (e.g. `~/Obsidian/Main/notes/capture`)
- `LECTUREN_DEFAULT_SUBFOLDER`
- `LECTUREN_ASR` default `local` or `openai`
- `LECTUREN_LLM` default `openai`, `groq`, or `local`

A user config file is stored at `~/.config/lecturen/config.yaml`. Paths are not hardcoded and can be overridden at runtime.

## Privacy

Local-first defaults. Only transcript chunks will be sent to cloud models when explicitly enabled.

## Roadmap

- M2: chunking, schema-constrained extraction to JSON, normalization, Markdown render
- M3: review TUI and sidecar selection JSON, final write to vault
- M4: optional screenshots, per-course defaults, tests and CI
