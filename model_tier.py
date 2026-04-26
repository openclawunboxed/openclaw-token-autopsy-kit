#!/usr/bin/env python3
"""
model tier classifier.

reads model_tier_map.csv and exposes a classify() helper. used by
heartbeat_audit.py and any other script that wants to flag premium models on
routine lanes without relying on brittle substring matching.

usage as a module:
    from model_tier import classify_model
    tier = classify_model("claude-sonnet-4-6")  # returns "mid"

usage as a script (debug):
    python model_tier.py claude-sonnet-4-6 gpt-4.1-mini openrouter/opus
"""
from __future__ import annotations

import csv
import sys
from pathlib import Path
from typing import Dict


_TIER_CACHE: Dict[str, str] | None = None


def _load(map_path: Path) -> Dict[str, str]:
    out: Dict[str, str] = {}
    if not map_path.exists():
        return out
    with map_path.open("r", encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            pattern = (row.get("model_pattern") or "").strip().lower()
            tier = (row.get("tier") or "").strip().lower()
            if pattern and tier:
                out[pattern] = tier
    return out


def _get_map(map_path: Path | None = None) -> Dict[str, str]:
    global _TIER_CACHE
    if _TIER_CACHE is None:
        path = map_path or (Path(__file__).resolve().parent / "model_tier_map.csv")
        _TIER_CACHE = _load(path)
    return _TIER_CACHE


def classify_model(model: str, map_path: Path | None = None) -> str:
    """
    return one of: premium, mid, budget, unknown.

    matching strategy:
        1. exact match against the tier map
        2. prefix match (any tier map entry that the model starts with)
        3. substring fallback for legacy aliases (opus/sonnet/haiku/gpt-5/gpt-4.1)
        4. unknown
    """
    if not model:
        return "unknown"
    key = model.strip().lower()
    tier_map = _get_map(map_path)

    if key in tier_map:
        return tier_map[key]

    # prefix match: longest pattern wins
    candidates = sorted(
        [p for p in tier_map if p != "default" and (key.startswith(p) or p in key)],
        key=len, reverse=True,
    )
    if candidates:
        return tier_map[candidates[0]]

    # substring fallback for older or aliased names
    if "opus" in key or "gpt-5" in key.replace("-mini", "").replace("-nano", ""):
        return "premium"
    if "sonnet" in key or "gpt-4.1" == key or "gpt-4o" == key:
        return "mid"
    if "haiku" in key or "mini" in key or "nano" in key or "flash" in key or "8b" in key or "4b" in key:
        return "budget"

    return tier_map.get("default", "unknown")


def main() -> None:
    if len(sys.argv) < 2:
        print("usage: python model_tier.py <model_name> [<model_name> ...]")
        sys.exit(1)
    for model in sys.argv[1:]:
        tier = classify_model(model)
        print(f"{model}\t{tier}")


if __name__ == "__main__":
    main()
