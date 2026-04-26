#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
from pathlib import Path
from typing import Iterable

TEXT_SUFFIXES = {".md", ".txt", ".json", ".jsonl", ".csv", ".yaml", ".yml"}


def estimate_tokens(text: str) -> int:
    return max(1, int(len(text) / 4))


def iter_files(paths: Iterable[Path]):
    for path in paths:
        if path.is_dir():
            for child in path.rglob("*"):
                if child.is_file() and child.suffix.lower() in TEXT_SUFFIXES:
                    yield child
        elif path.is_file() and path.suffix.lower() in TEXT_SUFFIXES:
            yield path


def classify(path: Path) -> str:
    name = path.name.lower()
    if "memory" in name:
        return "memory"
    if "agent" in name or "soul" in name or "user" in name:
        return "bootstrap"
    if path.suffix.lower() == ".jsonl":
        return "log"
    return "general"


def main():
    parser = argparse.ArgumentParser(description="estimate file weight and likely prompt bloat")
    parser.add_argument("--paths", nargs="+", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    rows = []
    for file_path in iter_files([Path(p) for p in args.paths]):
        try:
            text = file_path.read_text(encoding="utf-8")
        except Exception:
            continue
        rows.append(
            {
                "path": str(file_path),
                "bytes": len(text.encode("utf-8")),
                "estimated_tokens": estimate_tokens(text),
                "class": classify(file_path),
                "risk": "high" if estimate_tokens(text) > 5000 else "medium" if estimate_tokens(text) > 1500 else "low",
            }
        )

    rows.sort(key=lambda x: x["estimated_tokens"], reverse=True)

    with Path(args.output).open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["path", "bytes", "estimated_tokens", "class", "risk"])
        writer.writeheader()
        writer.writerows(rows)

    print(f"wrote {args.output}")


if __name__ == "__main__":
    main()
