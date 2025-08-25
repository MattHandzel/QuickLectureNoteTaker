from pathlib import Path
import subprocess

def extract_wav_mono_16k(src_video: Path, out_wav: Path) -> None:
    out_wav.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        "ffmpeg",
        "-y",
        "-i",
        str(src_video),
        "-ac",
        "1",
        "-ar",
        "16000",
        "-vn",
        str(out_wav),
    ]
    subprocess.run(cmd, check=True)
