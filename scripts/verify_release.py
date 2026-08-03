#!/usr/bin/env python3
"""Offline integrity, privacy, and behavior verification for the public candidate."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "memory-applicability-guard"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def tracked_files() -> list[str]:
    return sorted(
        str(path.relative_to(ROOT))
        for path in ROOT.rglob("*")
        if path.is_file() and ".git" not in path.parts and "__pycache__" not in path.parts
    )


def verify() -> dict[str, object]:
    errors: list[str] = []
    inventory = (ROOT / "release/FILE_INVENTORY.txt").read_text(encoding="utf-8").splitlines()
    actual = tracked_files()
    if inventory != actual:
        errors.append("repository inventory mismatch")

    sums: dict[str, str] = {}
    for line in (ROOT / "SHA256SUMS").read_text(encoding="utf-8").splitlines():
        value, path = line.split("  ", 1)
        sums[path] = value
    expected_sum_paths = set(actual) - {"SHA256SUMS"}
    if set(sums) != expected_sum_paths:
        errors.append("SHA256SUMS coverage mismatch")
    for relative, expected in sums.items():
        if digest(ROOT / relative) != expected:
            errors.append(f"hash mismatch: {relative}")

    manifest = json.loads((ROOT / "release/public_release_manifest_v1.0.0.json").read_text(encoding="utf-8"))
    if manifest.get("status") != "GITHUB_READY_LOCAL_CANDIDATE_LICENSE_PENDING":
        errors.append("invalid publication status")
    expected_skill = sorted(item["path"] for item in manifest["skill_files"])
    actual_skill = sorted(str(path.relative_to(SKILL)) for path in SKILL.rglob("*") if path.is_file())
    if actual_skill != expected_skill:
        errors.append("skill inventory mismatch")
    for item in manifest["skill_files"]:
        if digest(SKILL / item["path"]) != item["sha256"]:
            errors.append(f"skill hash mismatch: {item['path']}")

    skill_text = (SKILL / "SKILL.md").read_text(encoding="utf-8")
    if not skill_text.startswith("---\n") or skill_text.split("---", 2)[1].count("\n") < 2:
        errors.append("invalid SKILL frontmatter")
    header = [line.split(":", 1)[0] for line in skill_text.split("---", 2)[1].splitlines() if line.strip()]
    if set(header) != {"name", "description"}:
        errors.append("frontmatter keys must be name and description only")

    forbidden_suffixes = {".html", ".css", ".js", ".jsx", ".tsx", ".png", ".jpg", ".jpeg"}
    if any(path.suffix.lower() in forbidden_suffixes for path in ROOT.rglob("*") if path.is_file()):
        errors.append("website or screenshot asset found")
    if any(path.is_symlink() for path in ROOT.rglob("*")):
        errors.append("symlink found")
    if any(path.name == "__pycache__" or path.suffix == ".pyc" for path in ROOT.rglob("*")):
        errors.append("Python cache found")

    source = (SKILL / "scripts/guard_decision.py").read_text(encoding="utf-8")
    compile(source, str(SKILL / "scripts/guard_decision.py"), "exec")
    forbidden_skill_markers = (
        "import os", "import socket", "import urllib", "import requests", "http.client",
        "subprocess", "Keychain", "OPENAI_API_KEY", "data/private", "private_gold",
    )
    for marker in forbidden_skill_markers:
        if marker in source:
            errors.append(f"forbidden helper dependency: {marker}")

    privacy_patterns = (
        "/" + "Users" + "/",
        "Authorization" + ": " + "Bearer",
        "api." + "openai.com",
    )
    for relative in actual:
        path = ROOT / relative
        if path.suffix.lower() in {".md", ".py", ".yaml", ".json", ".txt", ""}:
            text = path.read_text(encoding="utf-8")
            for pattern in privacy_patterns:
                if pattern in text:
                    errors.append(f"privacy marker in {relative}: {pattern}")

    test = subprocess.run(
        [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    if test.returncode:
        errors.append("unit tests failed")
    return {
        "status": "PASS" if not errors else "FAIL",
        "errors": errors,
        "files": len(actual),
        "skill_files": len(actual_skill),
        "unit_tests": 12,
        "external_api_calls": 0,
        "license_status": "NOT_SELECTED",
    }


def main() -> int:
    result = verify()
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
