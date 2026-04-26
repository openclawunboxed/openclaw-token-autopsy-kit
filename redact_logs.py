#!/usr/bin/env python3
"""
log redactor.

scrubs common pii and secret patterns from a log file before the file leaves
a client environment. consultants running the kit on someone else's data
should run this first, then run cost_ledger.py on the redacted copy.

what it scrubs:
    - email addresses
    - phone numbers (us and international shapes)
    - urls
    - bearer tokens, api keys, and obvious secret-looking strings
    - aws-shaped access keys
    - credit card shaped numbers
    - long quoted message content (collapsed to length only)

what it does not scrub:
    - model names, agent ids, session ids, tokens counts, costs

usage:
    python redact_logs.py --input client_logs.jsonl --output redacted.jsonl
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any, Dict


PATTERNS = [
    (re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"), "[email]"),
    (re.compile(r"\+?\d{1,3}[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}"), "[phone]"),
    (re.compile(r"https?://[^\s\"'<>]+"), "[url]"),
    (re.compile(r"sk-[a-zA-Z0-9]{20,}"), "[api_key]"),
    (re.compile(r"AKIA[0-9A-Z]{16}"), "[aws_access_key]"),
    (re.compile(r"Bearer\s+[a-zA-Z0-9._\-]{20,}"), "Bearer [token]"),
    (re.compile(r"\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b"), "[card]"),
]

LONG_TEXT_FIELDS = {"prompt", "completion", "response", "message", "content", "input", "output", "text"}


def redact_string(s: str) -> str:
    out = s
    for pat, replacement in PATTERNS:
        out = pat.sub(replacement, out)
    return out


def collapse_long_text(value: Any, max_chars: int) -> Any:
    if isinstance(value, str) and len(value) > max_chars:
        return f"[redacted_text_len={len(value)}]"
    return value


def redact_record(record: Dict[str, Any], collapse_max: int) -> Dict[str, Any]:
    out: Dict[str, Any] = {}
    for key, value in record.items():
        key_lower = key.lower()
        if key_lower in LONG_TEXT_FIELDS:
            value = collapse_long_text(value, collapse_max)
        if isinstance(value, str):
            out[key] = redact_string(value)
        elif isinstance(value, dict):
            out[key] = redact_record(value, collapse_max)
        elif isinstance(value, list):
            out[key] = [
                redact_record(v, collapse_max) if isinstance(v, dict)
                else (redact_string(v) if isinstance(v, str) else v)
                for v in value
            ]
        else:
            out[key] = value
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description="redact pii and secrets from openclaw logs before audit")
    parser.add_argument("--input", required=True, help="jsonl log file")
    parser.add_argument("--output", required=True, help="redacted jsonl output")
    parser.add_argument("--collapse-text-over", type=int, default=400,
                        help="collapse string fields longer than this in known content fields")
    args = parser.parse_args()

    in_path = Path(args.input)
    out_path = Path(args.output)
    count = 0
    with in_path.open("r", encoding="utf-8") as f_in, out_path.open("w", encoding="utf-8") as f_out:
        for line in f_in:
            line = line.strip()
            if not line:
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                f_out.write(redact_string(line) + "\n")
                count += 1
                continue
            redacted = redact_record(record, args.collapse_text_over)
            f_out.write(json.dumps(redacted) + "\n")
            count += 1

    print(f"wrote {out_path} ({count} records redacted)")


if __name__ == "__main__":
    main()
