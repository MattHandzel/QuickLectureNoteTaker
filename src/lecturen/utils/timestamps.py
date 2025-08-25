def seconds_to_timestamp(s: float) -> str:
    total = int(round(s))
    m = total // 60
    sec = total % 60
    return f"{m:02d}:{sec:02d}"

def timestamp_to_seconds(ts: str) -> float:
    parts = ts.split(":")
    if len(parts) != 2:
        return 0.0
    return int(parts[0]) * 60 + int(parts[1])
