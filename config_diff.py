#!/usr/bin/env python3
"""
openclaw config diff.

compares two openclaw config files and reports what changed in plain language,
focused on the fields that actually move spend: routing, heartbeat interval,
agent defaults, and cron settings.

usage:
    python config_diff.py --before old_config.json --after new_config.json --output config_diff.md
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any, Dict, List


def parse_json5_like(text: str) -> Dict[str, Any]:
    cleaned = re.sub(r"//.*?$", "", text, flags=re.MULTILINE)
    cleaned = re.sub(r",(\s*[}\]])", r"\1", cleaned)
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        return {}


def get(d: Dict[str, Any], path: str, default: Any = None) -> Any:
    keys = path.split(".")
    cur: Any = d
    for k in keys:
        if not isinstance(cur, dict):
            return default
        cur = cur.get(k, default)
    return cur


def diff_routing(before: Dict[str, Any], after: Dict[str, Any]) -> List[str]:
    lines = []
    b_routing = before.get("routing") or {}
    a_routing = after.get("routing") or {}
    keys = sorted(set(b_routing) | set(a_routing))
    for k in keys:
        bv = b_routing.get(k, "(unset)")
        av = a_routing.get(k, "(unset)")
        if bv != av:
            lines.append(f"- routing for `{k}`: `{bv}` -> `{av}`")
    return lines


def diff_models(before: Dict[str, Any], after: Dict[str, Any]) -> List[str]:
    lines = []
    b_models = before.get("models") or {}
    a_models = after.get("models") or {}
    keys = sorted(set(b_models) | set(a_models))
    for k in keys:
        bv = b_models.get(k, "(unset)")
        av = a_models.get(k, "(unset)")
        if bv != av:
            lines.append(f"- model lane `{k}`: `{bv}` -> `{av}`")
    return lines


def diff_heartbeat(before: Dict[str, Any], after: Dict[str, Any]) -> List[str]:
    lines = []
    b_top = get(before, "heartbeat.every", "(unset)")
    a_top = get(after, "heartbeat.every", "(unset)")
    if b_top != a_top:
        lines.append(f"- top-level heartbeat interval: `{b_top}` -> `{a_top}`")

    b_def = get(before, "agents.defaults.heartbeat.every", "(unset)")
    a_def = get(after, "agents.defaults.heartbeat.every", "(unset)")
    if b_def != a_def:
        lines.append(f"- agent default heartbeat interval: `{b_def}` -> `{a_def}`")
    return lines


def diff_cron(before: Dict[str, Any], after: Dict[str, Any]) -> List[str]:
    lines = []
    fields = [
        ("cron.enabled", "cron enabled"),
        ("cron.maxConcurrentRuns", "cron max concurrent runs"),
        ("cron.sessionRetention", "cron session retention"),
    ]
    for path, label in fields:
        bv = get(before, path, "(unset)")
        av = get(after, path, "(unset)")
        if bv != av:
            lines.append(f"- {label}: `{bv}` -> `{av}`")
    return lines


def explain_change(line: str) -> str:
    """add a one-line plain-language explanation under each change."""
    l = line.lower()
    if "heartbeat" in l and "interval" in l:
        return "  - longer interval reduces heartbeat row count linearly. shorter interval will increase spend."
    if "routing for `heartbeat`" in l:
        return "  - this is the lane that runs every interval. moving from premium to budget here is the single biggest cost lever in most stacks."
    if "routing for `tool_heavy`" in l:
        return "  - browser, screenshot, and pdf paths run here. premium models on this lane multiply fast."
    if "routing for `high_judgment`" in l or "routing for `default`" in l:
        return "  - this lane should usually keep a strong model. only change if you confirmed the work tolerates a downgrade."
    if "cron enabled" in l:
        return "  - cron lets exact-time work create task records and skip main-session context."
    if "cron max concurrent runs" in l:
        return "  - too high can spike spend during overlaps. too low can starve scheduled work."
    return ""


def main() -> None:
    parser = argparse.ArgumentParser(description="diff two openclaw config files in plain language")
    parser.add_argument("--before", required=True)
    parser.add_argument("--after", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    before = parse_json5_like(Path(args.before).read_text(encoding="utf-8"))
    after = parse_json5_like(Path(args.after).read_text(encoding="utf-8"))

    sections = [
        ("routing changes", diff_routing(before, after) + diff_models(before, after)),
        ("heartbeat changes", diff_heartbeat(before, after)),
        ("cron changes", diff_cron(before, after)),
    ]

    lines = ["# openclaw config diff", ""]
    any_change = False
    for title, items in sections:
        if not items:
            continue
        any_change = True
        lines.append(f"## {title}")
        lines.append("")
        for item in items:
            lines.append(item)
            explanation = explain_change(item)
            if explanation:
                lines.append(explanation)
        lines.append("")

    if not any_change:
        lines.append("no relevant changes detected. routing, heartbeat, and cron settings match.")

    Path(args.output).write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {args.output}")


if __name__ == "__main__":
    main()
