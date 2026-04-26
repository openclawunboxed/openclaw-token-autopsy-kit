#!/usr/bin/env python3
"""
tests for cost_ledger.py.

run with: python -m pytest tests/ -v
or: python tests/test_cost_ledger.py (uses unittest fallback for stdlib-only)
"""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from cost_ledger import (  # noqa: E402
    aggregate,
    infer_job_type,
    load_price_map,
    load_records,
    normalize,
    resolve_prices,
)


class TestInferJobType(unittest.TestCase):
    def test_heartbeat_detected(self):
        record = {"task": "heartbeat sync"}
        self.assertEqual(infer_job_type(record), "heartbeat")

    def test_cron_detected(self):
        record = {"task": "scheduled report"}
        self.assertEqual(infer_job_type(record), "cron")

    def test_tool_heavy_detected(self):
        record = {"task": "browser navigation"}
        self.assertEqual(infer_job_type(record), "tool_heavy")

    def test_general_fallback(self):
        record = {"task": "answer question"}
        self.assertEqual(infer_job_type(record), "general")

    def test_heartbeat_wins_over_browser(self):
        # both tokens present, heartbeat is checked first
        record = {"task": "heartbeat with browser tool"}
        self.assertEqual(infer_job_type(record), "heartbeat")


class TestResolvePrices(unittest.TestCase):
    def test_explicit_prices_in_record(self):
        record = {"input_price_per_1k": 0.005, "output_price_per_1k": 0.025}
        in_price, out_price = resolve_prices(record, {}, "any-model")
        self.assertEqual(in_price, 0.005)
        self.assertEqual(out_price, 0.025)

    def test_exact_match_in_price_map(self):
        price_map = {"claude-sonnet-4-6": (0.003, 0.015)}
        in_price, out_price = resolve_prices({}, price_map, "claude-sonnet-4-6")
        self.assertEqual(in_price, 0.003)
        self.assertEqual(out_price, 0.015)

    def test_case_insensitive_match(self):
        price_map = {"claude-sonnet-4-6": (0.003, 0.015)}
        in_price, out_price = resolve_prices({}, price_map, "Claude-Sonnet-4-6")
        self.assertEqual(in_price, 0.003)

    def test_wildcard_prefix_match(self):
        price_map = {"claude-sonnet-*": (0.003, 0.015)}
        in_price, out_price = resolve_prices({}, price_map, "claude-sonnet-4-6")
        self.assertEqual(in_price, 0.003)

    def test_default_fallback(self):
        price_map = {"default": (0.001, 0.005)}
        in_price, out_price = resolve_prices({}, price_map, "unknown-model")
        self.assertEqual(in_price, 0.001)

    def test_no_match_returns_zero(self):
        in_price, out_price = resolve_prices({}, {}, "unknown-model")
        self.assertEqual(in_price, 0.0)
        self.assertEqual(out_price, 0.0)


class TestNormalize(unittest.TestCase):
    def test_basic_record(self):
        record = {
            "agent": "ops",
            "session": "main",
            "model": "claude-sonnet-4-6",
            "job_type": "heartbeat",
            "input_tokens": 1000,
            "output_tokens": 100,
        }
        price_map = {"claude-sonnet-4-6": (0.003, 0.015)}
        result = normalize(record, price_map)
        self.assertEqual(result["agent"], "ops")
        self.assertEqual(result["model"], "claude-sonnet-4-6")
        self.assertEqual(result["job_type"], "heartbeat")
        self.assertEqual(result["total_tokens"], 1100)
        # cost: 1.0 * 0.003 + 0.1 * 0.015 = 0.0045
        self.assertAlmostEqual(result["cost_usd"], 0.0045, places=6)
        self.assertTrue(result["recurring"])

    def test_alternate_field_names(self):
        record = {
            "agent_id": "ops",
            "session_id": "main",
            "provider_model": "gpt-4.1-mini",
            "type": "general",
            "prompt_tokens": 500,
            "completion_tokens": 50,
        }
        result = normalize(record, {})
        self.assertEqual(result["agent"], "ops")
        self.assertEqual(result["session"], "main")
        self.assertEqual(result["model"], "gpt-4.1-mini")
        self.assertEqual(result["job_type"], "general")
        self.assertEqual(result["input_tokens"], 500)
        self.assertEqual(result["output_tokens"], 50)

    def test_recurring_inferred_from_job_type(self):
        record = {"job_type": "cron", "input_tokens": 100, "output_tokens": 10}
        result = normalize(record, {})
        self.assertTrue(result["recurring"])

    def test_recurring_false_for_general(self):
        record = {"job_type": "general", "input_tokens": 100, "output_tokens": 10}
        result = normalize(record, {})
        self.assertFalse(result["recurring"])

    def test_explicit_cost_overrides_calculation(self):
        record = {
            "model": "claude-sonnet-4-6",
            "input_tokens": 1000,
            "output_tokens": 100,
            "cost_usd": 99.99,
        }
        price_map = {"claude-sonnet-4-6": (0.003, 0.015)}
        result = normalize(record, price_map)
        self.assertEqual(result["cost_usd"], 99.99)

    def test_missing_tokens_default_to_zero(self):
        record = {"model": "x", "agent": "ops"}
        result = normalize(record, {})
        self.assertEqual(result["input_tokens"], 0)
        self.assertEqual(result["output_tokens"], 0)
        self.assertEqual(result["cost_usd"], 0.0)


class TestAggregate(unittest.TestCase):
    def test_two_runs_same_key_aggregate(self):
        rows = [
            normalize({"agent": "ops", "session": "main", "model": "x", "job_type": "heartbeat",
                       "input_tokens": 100, "output_tokens": 10, "cost_usd": 0.05}, {}),
            normalize({"agent": "ops", "session": "main", "model": "x", "job_type": "heartbeat",
                       "input_tokens": 200, "output_tokens": 20, "cost_usd": 0.10}, {}),
        ]
        result = aggregate(rows)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["runs"], 2)
        self.assertEqual(result[0]["input_tokens"], 300)
        self.assertEqual(result[0]["output_tokens"], 30)
        self.assertAlmostEqual(result[0]["cost_usd"], 0.15, places=6)

    def test_different_keys_stay_separate(self):
        rows = [
            normalize({"agent": "ops", "session": "a", "model": "x", "job_type": "heartbeat",
                       "input_tokens": 100, "output_tokens": 10, "cost_usd": 0.05}, {}),
            normalize({"agent": "ops", "session": "b", "model": "x", "job_type": "heartbeat",
                       "input_tokens": 100, "output_tokens": 10, "cost_usd": 0.05}, {}),
        ]
        result = aggregate(rows)
        self.assertEqual(len(result), 2)

    def test_sorted_by_cost_descending(self):
        rows = [
            normalize({"agent": "a", "model": "x", "input_tokens": 100, "output_tokens": 10,
                       "cost_usd": 0.01}, {}),
            normalize({"agent": "b", "model": "x", "input_tokens": 100, "output_tokens": 10,
                       "cost_usd": 0.99}, {}),
            normalize({"agent": "c", "model": "x", "input_tokens": 100, "output_tokens": 10,
                       "cost_usd": 0.50}, {}),
        ]
        result = aggregate(rows)
        self.assertEqual(result[0]["agent"], "b")
        self.assertEqual(result[-1]["agent"], "a")


class TestLoadRecords(unittest.TestCase):
    def test_jsonl(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as f:
            f.write('{"a": 1}\n{"a": 2}\n\n{"a": 3}\n')
            path = Path(f.name)
        try:
            records = load_records(path)
            self.assertEqual(len(records), 3)
            self.assertEqual(records[0]["a"], 1)
        finally:
            path.unlink()

    def test_json_list(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump([{"a": 1}, {"a": 2}], f)
            path = Path(f.name)
        try:
            records = load_records(path)
            self.assertEqual(len(records), 2)
        finally:
            path.unlink()

    def test_json_with_runs_key(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump({"runs": [{"a": 1}, {"a": 2}]}, f)
            path = Path(f.name)
        try:
            records = load_records(path)
            self.assertEqual(len(records), 2)
        finally:
            path.unlink()

    def test_csv(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            f.write("model,input_tokens,output_tokens\nx,100,10\ny,200,20\n")
            path = Path(f.name)
        try:
            records = load_records(path)
            self.assertEqual(len(records), 2)
            self.assertEqual(records[0]["model"], "x")
        finally:
            path.unlink()

    def test_unsupported_extension_raises(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("hello")
            path = Path(f.name)
        try:
            with self.assertRaises(ValueError):
                load_records(path)
        finally:
            path.unlink()


class TestLoadPriceMap(unittest.TestCase):
    def test_basic_load(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            f.write("model,input_price_per_1k,output_price_per_1k\nclaude-sonnet-4-6,0.003,0.015\n")
            path = Path(f.name)
        try:
            price_map = load_price_map(path)
            self.assertEqual(price_map["claude-sonnet-4-6"], (0.003, 0.015))
        finally:
            path.unlink()

    def test_missing_file_returns_empty(self):
        price_map = load_price_map(Path("/nonexistent/path.csv"))
        self.assertEqual(price_map, {})


if __name__ == "__main__":
    unittest.main()
