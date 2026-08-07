#!/usr/bin/env python3
from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path

from project_status_v2 import AUTHORITY, StatusError, initial_record, validate, write_record


class ProjectStatusV2Tests(unittest.TestCase):
    def setUp(self) -> None:
        self.record = initial_record("owner/example", "Example")

    def test_initial_record_is_truthfully_insufficient(self) -> None:
        validate(self.record)
        self.assertEqual(0, self.record["percentage_complete"]["estimate"])
        self.assertEqual("insufficient", self.record["lifecycle_status"]["verified"])
        self.assertEqual(AUTHORITY, self.record["lifecycle_status"]["authority"])
        self.assertFalse(any(stage["result"] == "PASS" for stage in self.record["lifecycle_status"]["stages"]))

    def test_percentage_cannot_create_completion(self) -> None:
        record = copy.deepcopy(self.record)
        record["percentage_complete"]["estimate"] = 100
        record["lifecycle_status"]["verified"] = "complete"
        with self.assertRaisesRegex(StatusError, "complete requires direct PASS"):
            validate(record)

    def test_proxy_pass_is_rejected(self) -> None:
        record = copy.deepcopy(self.record)
        stage = record["lifecycle_status"]["stages"][0]
        stage.update(result="PASS", relationship="proxy", evidence=["fixture"])
        with self.assertRaisesRegex(StatusError, "requires direct evidence"):
            validate(record)

    def test_environment_mismatch_is_rejected(self) -> None:
        record = copy.deepcopy(self.record)
        stage = record["lifecycle_status"]["stages"][0]
        stage.update(result="PASS", relationship="direct", evidence=["issue:1"], observed_environment="fixture")
        with self.assertRaisesRegex(StatusError, "environment mismatch"):
            validate(record)

    def test_output_is_deterministic(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            first = Path(directory) / "first.json"
            second = Path(directory) / "second.json"
            write_record(first, "owner/example", "Example")
            write_record(second, "owner/example", "Example")
            self.assertEqual(first.read_bytes(), second.read_bytes())

    def test_output_contains_no_private_control_plane_data(self) -> None:
        text = json.dumps(self.record)
        for fragment in ("I:\\", "C:\\", "GH_TOKEN", "GITHUB_TOKEN", "sk-", "private inventory"):
            self.assertNotIn(fragment.lower(), text.lower())

    def test_wrong_authority_is_rejected(self) -> None:
        record = copy.deepcopy(self.record)
        record["lifecycle_status"]["authority"] = "latest"
        with self.assertRaisesRegex(StatusError, "pinned shared control"):
            validate(record)


if __name__ == "__main__":
    unittest.main()
