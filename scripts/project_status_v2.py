#!/usr/bin/env python3
"""Generate and validate the version-pinned initial Project Status v2 record."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

AUTHORITY = "armpitpete/merrin-project-controls@7bc8b7f5ef921851ad163093f089d28d8128bf6c"
STAGES = (
    "designed",
    "implemented",
    "automated-checks",
    "independent-review",
    "merged",
    "deployed",
    "live-behaviour",
    "human-acceptance",
)
FORBIDDEN_FRAGMENTS = ("I:\\", "C:\\", "GH_TOKEN", "GITHUB_TOKEN", "sk-", "private inventory")


class StatusError(ValueError):
    pass


def initial_record(repository: str, project_name: str) -> dict[str, Any]:
    stages: list[dict[str, Any]] = []
    for stage in STAGES:
        if stage == "designed":
            stages.append({
                "stage": stage,
                "required": True,
                "required_environment": "accepted project authority",
                "result": "INSUFFICIENT",
                "relationship": "missing",
                "evidence": [],
                "limitations": ["No accepted project-specific authority evidence has been recorded yet."],
            })
        else:
            stages.append({
                "stage": stage,
                "required": False,
                "rationale": "This initial bootstrap record makes no claim for this later lifecycle stage.",
                "result": "NOT_APPLICABLE",
                "relationship": "not-applicable",
                "evidence": [],
                "limitations": [],
            })
    return {
        "project": repository,
        "finish_line": f"Define and evidence the first bounded finish line for {project_name}.",
        "percentage_complete": {
            "estimate": 0,
            "confidence": "high",
            "evidence": ["Only repository bootstrap has occurred; project work is not counted as complete."],
            "remaining_work": ["Accept a bounded project authority and record direct lifecycle evidence."],
            "blockers": [],
        },
        "completion_likelihood": {
            "assessment": "possible",
            "confidence": "low",
            "reasons": ["The project has been created, but its first accepted finish line is not yet evidenced."],
        },
        "lifecycle_status": {
            "claimed": "designed",
            "verified": "insufficient",
            "authority": AUTHORITY,
            "limitations": ["Generated bootstrap fixture; not deployment, live-behaviour or acceptance evidence."],
            "stages": stages,
        },
        "next_bounded_action": "Assess and inventory source material without modifying it, then accept one bounded project authority.",
    }


def validate(record: Any) -> None:
    if not isinstance(record, dict):
        raise StatusError("project status must be an object")
    required = {"project", "finish_line", "percentage_complete", "completion_likelihood", "lifecycle_status", "next_bounded_action"}
    missing = sorted(required - set(record))
    if missing:
        raise StatusError("missing fields: " + ", ".join(missing))
    status = record["lifecycle_status"]
    if status.get("authority") != AUTHORITY:
        raise StatusError("project status authority is not the pinned shared control")
    stages = status.get("stages")
    if not isinstance(stages, list) or [item.get("stage") for item in stages] != list(STAGES):
        raise StatusError("all eight lifecycle stages must appear once in canonical order")
    for item in stages:
        if item.get("required"):
            if item.get("result") in {"PASS", "FAIL"}:
                if item.get("relationship") != "direct" or not item.get("evidence"):
                    raise StatusError(f"{item['stage']} PASS/FAIL requires direct evidence")
                if item.get("observed_environment") != item.get("required_environment"):
                    raise StatusError(f"{item['stage']} environment mismatch")
            elif item.get("result") != "INSUFFICIENT":
                raise StatusError(f"{item['stage']} required result is invalid")
        else:
            if item.get("result") != "NOT_APPLICABLE" or item.get("relationship") != "not-applicable" or not item.get("rationale"):
                raise StatusError(f"{item['stage']} not-applicable state is invalid")
    if status.get("verified") == "complete":
        if not all((not item["required"]) or (item["result"] == "PASS" and item["relationship"] == "direct") for item in stages):
            raise StatusError("complete requires direct PASS evidence for every required stage")
    text = json.dumps(record, sort_keys=True)
    for fragment in FORBIDDEN_FRAGMENTS:
        if fragment.lower() in text.lower():
            raise StatusError(f"privacy-sensitive fragment present: {fragment}")


def write_record(path: Path, repository: str, project_name: str) -> None:
    record = initial_record(repository, project_name)
    validate(record)
    path.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repository", required=True)
    parser.add_argument("--project-name", required=True)
    parser.add_argument("--output", default="project-status.json")
    parser.add_argument("--validate-only", action="store_true")
    args = parser.parse_args()
    path = Path(args.output)
    if args.validate_only:
        validate(json.loads(path.read_text(encoding="utf-8")))
    else:
        write_record(path, args.repository, args.project_name)
    print(f"valid Project Status v2: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
