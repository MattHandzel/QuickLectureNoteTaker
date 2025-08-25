from pathlib import Path
import json
import orjson
import tempfile
import shutil

def ensure_dir(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)

def write_text(path: Path, text: str) -> None:
    ensure_dir(path.parent)
    with tempfile.NamedTemporaryFile("w", delete=False, dir=str(path.parent), encoding="utf-8") as tmp:
        tmp.write(text)
        tmp_path = Path(tmp.name)
    tmp_path.replace(path)

def write_json(path: Path, obj) -> None:
    ensure_dir(path.parent)
    data = orjson.dumps(obj)
    with tempfile.NamedTemporaryFile("wb", delete=False, dir=str(path.parent)) as tmp:
        tmp.write(data)
        tmp_path = Path(tmp.name)
    tmp_path.replace(path)

def read_json(path: Path):
    with path.open("rb") as f:
        return orjson.loads(f.read())

def copy_file(src: Path, dst: Path) -> None:
    ensure_dir(dst.parent)
    shutil.copy2(src, dst)
