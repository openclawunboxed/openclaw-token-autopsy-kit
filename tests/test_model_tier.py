#!/usr/bin/env python3
"""tests for model_tier.py."""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from model_tier import classify_model  # noqa: E402


class TestClassifyModel(unittest.TestCase):
    def test_premium_opus(self):
        self.assertEqual(classify_model("claude-opus-4-7"), "premium")
        self.assertEqual(classify_model("claude-opus-4-6"), "premium")

    def test_mid_sonnet(self):
        self.assertEqual(classify_model("claude-sonnet-4-6"), "mid")
        self.assertEqual(classify_model("claude-sonnet-4-5"), "mid")

    def test_budget_haiku(self):
        self.assertEqual(classify_model("claude-haiku-4-5"), "budget")

    def test_premium_gpt5(self):
        self.assertEqual(classify_model("gpt-5"), "premium")

    def test_budget_gpt5_nano(self):
        self.assertEqual(classify_model("gpt-5-nano"), "budget")

    def test_budget_gpt41_mini(self):
        self.assertEqual(classify_model("gpt-4.1-mini"), "budget")

    def test_openrouter_routing(self):
        self.assertEqual(classify_model("openrouter/opus"), "premium")
        self.assertEqual(classify_model("openrouter/sonnet"), "mid")

    def test_local_models(self):
        self.assertEqual(classify_model("local/qwen3-8b"), "budget")
        self.assertEqual(classify_model("local/llama"), "budget")

    def test_case_insensitive(self):
        self.assertEqual(classify_model("Claude-Opus-4-7"), "premium")

    def test_empty_string(self):
        self.assertEqual(classify_model(""), "unknown")

    def test_unknown_model_falls_back(self):
        # truly unknown should not crash
        result = classify_model("some-totally-made-up-model-xyz")
        self.assertIn(result, {"unknown", "premium", "mid", "budget"})


if __name__ == "__main__":
    unittest.main()
