#!/usr/bin/env python3
"""Build and validate an offline annotation workspace without model calls."""
from __future__ import annotations

import argparse
from datetime import datetime
import hashlib
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "memory-applicability-guard"
SPEC = importlib.util.spec_from_file_location("guard_review", SKILL / "scripts/guard_decision.py")
assert SPEC and SPEC.loader
GUARD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(GUARD)
PROTOCOL = "skill-p2-v1.1.0"
PUBLIC_FIELDS = {
    "applicability_boundary_metadata", "available_actions", "candidate_memories",
    "current_query", "eval_id", "interaction_history", "pack_version",
    "query_context", "query_date", "task_risk",
}
TARGET_FIELDS = {
    "permission", "relationship", "evidence_status", "risk",
    "robust_action_available", "robust_action", "decisive_evidence_ids",
    "memory_action",
}
ENUMS = {
    "permission": sorted(GUARD.PERMISSIONS), "relationship": sorted(GUARD.RELATIONSHIPS),
    "evidence_status": sorted(GUARD.EVIDENCE_STATUSES), "risk": sorted(GUARD.RISKS),
    "memory_action": sorted(GUARD.MEMORY_ACTIONS), "evidence_kind": sorted(GUARD.EVIDENCE_KINDS),
}


def load_public(path: Path, expected_hash: str) -> tuple[list[dict], str]:
    raw = path.read_bytes()
    actual = hashlib.sha256(raw).hexdigest()
    if actual != expected_hash:
        raise ValueError("Public source fingerprint mismatch; no override is available")
    rows = [json.loads(line) for line in raw.splitlines() if line.strip()]
    ids = set()
    if not rows:
        raise ValueError("Public source is empty")
    for row in rows:
        if not isinstance(row, dict) or set(row) != PUBLIC_FIELDS:
            raise ValueError("Public input field allowlist mismatch")
        identifier = row["eval_id"]
        if not isinstance(identifier, str) or not identifier or identifier in ids:
            raise ValueError("Public input IDs must be nonempty and unique")
        ids.add(identifier)
        if not isinstance(row["candidate_memories"], list) or len(row["candidate_memories"]) != 1:
            raise ValueError("This protocol requires exactly one candidate per case")
        evidence_records(row)
    return rows, actual


def evidence_records(row: dict) -> list[dict]:
    records = []
    for field, id_field in (("candidate_memories", "memory_id"), ("interaction_history", "entry_id"), ("applicability_boundary_metadata", "boundary_id")):
        if not isinstance(row[field], list):
            raise ValueError("Public evidence collections must be arrays")
        for item in row[field]:
            if not isinstance(item, dict) or not isinstance(item.get(id_field), str) or not item[id_field]:
                raise ValueError("Public evidence record has no valid ID")
            records.append({"id": item[id_field], "collection": field, "record": item})
    if len({item["id"] for item in records}) != len(records):
        raise ValueError("Evidence IDs must be unique within each case")
    return records


def blank_bundle(rows: list[dict], source_hash: str) -> dict:
    return {
        "protocol_version": PROTOCOL, "source_sha256": source_hash,
        "cases": [{"eval_id": row["eval_id"], "targets": {field: None for field in sorted(TARGET_FIELDS)},
                   "evidence_kinds": {}, "review": {"status": "DRAFT", "reviewer": None, "reviewed_at": None},
                   "notes": ""} for row in rows],
    }


def validate_bundle(bundle: dict, rows: list[dict], source_hash: str, require_reviewed: bool = False) -> dict:
    errors = []
    if not isinstance(bundle, dict) or set(bundle) != {"protocol_version", "source_sha256", "cases"}:
        return {"status": "FAIL", "errors": ["Invalid review bundle structure"], "reviewed": 0, "total": len(rows)}
    if bundle["protocol_version"] != PROTOCOL or bundle["source_sha256"] != source_hash:
        errors.append("Review bundle protocol or source fingerprint mismatch")
    entries = bundle["cases"]
    if not isinstance(entries, list):
        return {"status": "FAIL", "errors": errors + ["Review cases must be an array"], "reviewed": 0, "total": len(rows)}
    expected = {row["eval_id"]: row for row in rows}
    seen = set()
    reviewed = 0
    for entry in entries:
        if not isinstance(entry, dict) or set(entry) != {"eval_id", "targets", "evidence_kinds", "review", "notes"}:
            errors.append("Invalid target record structure")
            continue
        identifier = entry["eval_id"]
        if not isinstance(identifier, str) or identifier not in expected or identifier in seen:
            errors.append("Unknown or duplicate target case ID")
            continue
        seen.add(identifier)
        row = expected[identifier]
        targets, kinds, review = entry["targets"], entry["evidence_kinds"], entry["review"]
        prefix = f"{identifier}: "
        if not isinstance(targets, dict) or set(targets) != TARGET_FIELDS:
            errors.append(prefix + "Invalid target fields")
            continue
        if not isinstance(review, dict) or set(review) != {"status", "reviewer", "reviewed_at"} or not isinstance(review["status"], str) or review["status"] not in {"DRAFT", "REVIEWED"}:
            errors.append(prefix + "Invalid review record")
            continue
        known = {item["id"] for item in evidence_records(row)}
        if not isinstance(kinds, dict) or set(kinds) - known or any(not isinstance(v, str) or v not in GUARD.EVIDENCE_KINDS for v in kinds.values()):
            errors.append(prefix + "Unknown evidence IDs or kinds")
            continue
        if not isinstance(entry["notes"], str):
            errors.append(prefix + "Notes must be text")
        for field in ("permission", "relationship", "evidence_status", "risk", "memory_action"):
            if targets[field] is not None and (not isinstance(targets[field], str) or targets[field] not in ENUMS[field]):
                errors.append(prefix + f"Invalid {field} target")
        if targets["robust_action_available"] is not None and not isinstance(targets["robust_action_available"], bool):
            errors.append(prefix + "Robust availability must be a boolean or null")
        if targets["robust_action"] is not None and not isinstance(targets["robust_action"], str):
            errors.append(prefix + "Robust action must be text or null")
        draft_ids = targets["decisive_evidence_ids"]
        if draft_ids is not None:
            if not isinstance(draft_ids, list) or any(not isinstance(x, str) for x in draft_ids):
                errors.append(prefix + "Decisive IDs must be an array of strings or null")
            elif len(set(draft_ids)) != len(draft_ids) or set(draft_ids) - set(kinds):
                errors.append(prefix + "Decisive IDs must be unique and have supplied evidence kinds")
        if review["status"] == "DRAFT" and not require_reviewed:
            continue  # Incomplete drafts are preserved, never counted as accepted targets.
        if review["status"] != "REVIEWED":
            errors.append(prefix + "Human review is pending")
            continue
        if any(not isinstance(review[key], str) or not review[key].strip() for key in ("reviewer", "reviewed_at")):
            errors.append(prefix + "Reviewer and review timestamp are required")
        try:
            timestamp = datetime.fromisoformat(str(review["reviewed_at"]).replace("Z", "+00:00"))
            if timestamp.tzinfo is None or timestamp.utcoffset() is None:
                raise ValueError("Timezone missing")
        except ValueError:
            errors.append(prefix + "Review timestamp must be ISO 8601 with a timezone")
        for field in ("permission", "relationship", "evidence_status", "risk", "memory_action"):
            if not isinstance(targets[field], str) or targets[field] not in ENUMS[field]:
                errors.append(prefix + f"Invalid {field} target")
        if not isinstance(targets["robust_action_available"], bool):
            errors.append(prefix + "Robust availability must be a boolean")
        decisive = targets["decisive_evidence_ids"]
        if not isinstance(decisive, list) or any(not isinstance(x, str) for x in decisive):
            errors.append(prefix + "Decisive IDs must be an array of strings")
            continue
        if len(set(decisive)) != len(decisive) or set(decisive) - set(kinds):
            errors.append(prefix + "Decisive IDs must be unique and have supplied evidence kinds")
            continue
        payload = {"current_task": row["current_query"], "candidate_memory": row["candidate_memories"][0]["content"],
                   "proposed_memory_action": "USE", **{k: targets[k] for k in ("permission", "relationship", "evidence_status", "risk", "robust_action_available", "robust_action")},
                   "evidence": [{"id": k, "text": json.dumps(next(item["record"] for item in evidence_records(row) if item["id"] == k), ensure_ascii=False),
                                 "kind": v, "decisive": k in decisive} for k, v in kinds.items()]}
        try:
            result = GUARD.decide(payload)
            if result["memory_action"] != targets["memory_action"]:
                errors.append(prefix + "Expected memory action disagrees with the frozen helper policy; resolve before acceptance")
        except GUARD.InputValidationError as error:
            errors.append(prefix + error.code)
        reviewed += 1
    if seen != set(expected):
        errors.append("Targets do not cover exactly the source cases")
    return {"status": "FAIL" if errors else "PASS", "errors": errors, "reviewed": reviewed, "total": len(rows),
            "execution_ready": not errors and reviewed == len(rows),
            "boundary": "Human review is recorded, not independently authenticated by this tool."}


def build_html(rows: list[dict], source_hash: str) -> str:
    data = {"source_sha256": source_hash, "rows": rows, "bundle": blank_bundle(rows, source_hash),
            "enums": ENUMS, "evidence": [evidence_records(row) for row in rows]}
    encoded = json.dumps(data, ensure_ascii=False).replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")
    template = (ROOT / "evaluation/review.html").read_text()
    return template.replace("__REVIEW_DATA__", encoded)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("build", "validate"))
    parser.add_argument("--public-pack", type=Path, required=True)
    parser.add_argument("--source-sha256", required=True)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--targets", type=Path)
    parser.add_argument("--require-reviewed", action="store_true")
    args = parser.parse_args()
    try:
        rows, source_hash = load_public(args.public_pack, args.source_sha256)
        if args.command == "build":
            if args.output is None:
                parser.error("build requires --output")
            if args.output.exists():
                raise ValueError("Output already exists; use a new versioned filename")
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(build_html(rows, source_hash), encoding="utf-8")
            print(json.dumps({"status": "PASS", "cases": len(rows), "human_review": "PENDING", "model_calls": 0}))
            return 0
        if args.targets is None:
            parser.error("validate requires --targets")
        result = validate_bundle(json.loads(args.targets.read_text()), rows, source_hash, args.require_reviewed)
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0 if result["status"] == "PASS" else 2
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(json.dumps({"status": "FAIL", "error": str(error)}))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
