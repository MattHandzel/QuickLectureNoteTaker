import os
from pathlib import Path
import yaml

DEFAULTS = {
    "vault_path": str(Path.home() / "Obsidian" / "Main" / "notes" / "capture"),
    "default_subfolder": "capture",
    "asr": "local",
    "llm": "openai",
    "chunk_chars": 4000,
    "overlap_seconds": 8,
    "screenshots": False,
}

def config_dir() -> Path:
    return Path.home() / ".config" / "lecturen"

def config_path() -> Path:
    return config_dir() / "config.yaml"

def load_config() -> dict:
    p = config_path()
    if p.exists():
        with p.open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
    else:
        data = {}
    env_overrides = {
        "vault_path": os.environ.get("LECTUREN_VAULT_PATH"),
        "default_subfolder": os.environ.get("LECTUREN_DEFAULT_SUBFOLDER"),
        "asr": os.environ.get("LECTUREN_ASR"),
        "llm": os.environ.get("LECTUREN_LLM"),
    }
    merged = {**DEFAULTS, **data}
    for k, v in env_overrides.items():
        if v:
            merged[k] = v
    return merged

def save_config(cfg: dict) -> None:
    config_dir().mkdir(parents=True, exist_ok=True)
    with config_path().open("w", encoding="utf-8") as f:
        yaml.safe_dump(cfg, f)
