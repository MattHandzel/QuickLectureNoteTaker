from pathlib import Path
import re
import subprocess
import uuid
from datetime import datetime
from .utils.io import ensure_dir, copy_file
from .models import SessionMeta

def is_url(s: str) -> bool:
    return bool(re.match(r"^https?://", s.strip(), re.IGNORECASE))

def new_session_id() -> str:
    ts = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    suf = uuid.uuid4().hex[:6]
    return f"{ts}-{suf}"

def session_root(base: Path, session_id: str) -> Path:
    return base / "sessions" / session_id

def prepare_workspace(input_path_or_url: str, repo_root: Path) -> tuple[Path, SessionMeta]:
    base = repo_root / ".lecturen"
    ensure_dir(base)
    sid = new_session_id()
    root = session_root(base, sid)
    src_dir = root / "source"
    ensure_dir(src_dir)
    if is_url(input_path_or_url):
        out_template = src_dir / "%(title)s.%(ext)s"
        cmd = ["yt-dlp", "-o", str(out_template), input_path_or_url]
        subprocess.run(cmd, check=True)
        files = list(src_dir.glob("*"))
        if not files:
            raise RuntimeError("Download failed")
        source_path = files[0]
    else:
        p = Path(input_path_or_url).expanduser().resolve()
        if not p.exists():
            raise FileNotFoundError(str(p))
        dest = src_dir / p.name
        copy_file(p, dest)
        source_path = dest
    meta = SessionMeta(session_id=sid, source=str(source_path))
    ensure_dir(root / "audio")
    ensure_dir(root / "transcript")
    return root, meta
