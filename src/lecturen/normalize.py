from __future__ import annotations
from typing import List
from rapidfuzz import fuzz
from .models import AtomicNote

def _similar(a: str, b: str) -> int:
    return fuzz.token_set_ratio(a, b)

def dedupe_and_merge(items: List[AtomicNote], title_threshold: int = 90, body_threshold: int = 85) -> List[AtomicNote]:
    kept: List[AtomicNote] = []
    for item in items:
        dup = False
        for k in kept:
            if item.type == k.type:
                if _similar(item.title, k.title) >= title_threshold or _similar(item.body, k.body) >= body_threshold:
                    dup = True
                    break
        if not dup:
            kept.append(item)
    return kept
