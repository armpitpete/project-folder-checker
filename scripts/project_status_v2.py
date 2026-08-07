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
STATUS_TO_STAGE = {
    "designed": "designed",
    "implemented": "implemented",
    "automated-checks-passed": "automated-checks",
    "independently-reviewed": "independent-review",
    "merged": "merged",
    "deployed": "deployed",
    "live-behaviour-verified": "live-behaviour",
    "human-acceptance-received": "human-acceptance",
}
REQUIRED_ENVIRONMENTS = {
    "designed": "accepted project authority",
    "implemented": "exact implementation commit",
    "automated-checks": "exact-head automated checks",
    "independent-review": "exact-head independent review",
    "merged": "default-branch commit",
    "deployed": "declared deployment environment",
    "live-behaviour": "actual live environment",
    "human-acceptance": "declared human acceptance environment",
}
FORBIDDEN_FRAGMENTS = ("I:\\", "C:\\", "GH_TOKEN", "GITHUB_TOKEN", "sk-", "private inventory")


class StatusError(ValueError):
    pass


def initial_record(repository: str, project_name: str) -> dict[str, Any]:
    stages = [
        {
            "stage": stage,
            "required": True,
            "required_environment": REQUIRED_ENVIRONMENTS[stage],
            "result": "INSUFFICIENT",
            "relationship": "missing",
            "evidence": [],
            "limitations": [f"No direct {stage} evidence has been recorded yet."],
        }
        for stage in STAGES
    ]
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
            "limitations": ["Generated bootstrap fixture; not implementation, deployment, live-behaviour or acceptance evidence."],
            "stages": stages,
        },
        "next_bounded_action": "Assess and inventory source material without modifying it, then accept one bounded project authority.",
    }


def _expected_verified(claimed: str, stages: dict[str, dict[str, Any]]) -> str:
    relevant = list(STAGES) if claimed == "complete" else list(STAGES[: STAGES.index(STATUS_TO_STAGE[claimed]) + 1])
    if any(stages[name]["result"] == "FAIL" for name in relevant):
        return "failed"
    if all(
        stages[name]["result"] == "PASS"
        and stages[name]["relationship"] == "direct"
        and stages[name].get("observed_environment") == stages[name].get("required_environment")
        for name in relevant
    ):
        return "complete" if claimed == "complete" else claimed
    return "insufficient"


def validate(record: Any) -> None:
    if not isinstance(record, dict):
        raise StatusError("project status must be an object")
    required_fields = {"project", "finish_line", "percentage_complete", "completion_likelihood", "lifecycle_status", "next_bounded_action"}
    missing = sorted(required_fields - set(record))
    if missing:
        raise StatusError("missing fields: " + ", ".join(missing))

    status = record["lifecycle_status"]
    if status.get("authority") != AUTHORITY:
        raise StatusError("project status authority is not the pinned shared control")
    claimed = status.get("claimed")
    if claimed not in set(STATUS_TO_STAGE) | {"complete"}:
        raise StatusError("unsupported lifecycle claim")
    raw_stages = status.get("stages")
    if not isinstance(raw_stages, list) or [item.get("stage") for item in raw_stages] != list(STAGES):
        raise StatusError("all eight lifecycle stages must appear once in canonical order")

    stages: dict[str, dict[str, Any]] = {}
    for item in raw_stages:
        name = item["stage"]
        if item.get("required") is not True:
            raise StatusError(f"bootstrap lifecycle stage {name} must remain required")
        if item.get("required_environment") != REQUIRED_ENVIRONMENTS[name]:
            raise StatusError(f"{name} required environment does not match the pinned bootstrap contract")
        result = item.get("result")
        relationship = item.get("relationship")
        evidence = item.get("evidence", [])
        if result in {"PASS", "FAIL"}:
            if relationship != "direct" or not evidence:
                raise StatusError(f"{name} PASS/FAIL requires direct evidence")
            if item.get("observed_environment") != item.get("required_environment"):
                raise StatusError(f"{name} environment mismatch")
        elif result == "INSUFFICIENT":
            if relationship not in {"direct", "proxy", "missing"}:
                raise StatusError(f"{name} INSUFFICIENT relationship is invalid")
        else:
            raise StatusError(f"{name} required result is invalid")
        stages[name] = item

    expected = _expected_verified(claimed, stages)
    if status.get("verified") != expected:
        raise StatusError(f"lifecycle_status.verified must be {expected!r}")

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
