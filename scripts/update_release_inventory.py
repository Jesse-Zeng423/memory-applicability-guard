#!/usr/bin/env python3
"""Rewrite FILE_INVENTORY.txt, SHA256SUMS, and Skill hashes from the current tree."""

from __future__ import annotations

import json
import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))
from verify_release import ROOT, SKILL, digest, tracked_files  # noqa: E402


def main() -> int:
    files = tracked_files()
    (ROOT / "release/FILE_INVENTORY.txt").write_text("\n".join(files) + "\n", encoding="utf-8")
    files = tracked_files()
    sums = [f"{digest(ROOT / relative)}  {relative}" for relative in files if relative != "SHA256SUMS"]
    (ROOT / "SHA256SUMS").write_text("\n".join(sums) + "\n", encoding="utf-8")

    manifest_path = ROOT / "release/public_release_manifest_v1.0.0.json"
    text = manifest_path.read_text(encoding="utf-8")
    manifest = json.loads(text)
    for item in manifest["skill_files"]:
        new_hash = digest(SKILL / item["path"])
        text = text.replace(item["sha256"], new_hash, 1)
        item["sha256"] = new_hash
    manifest_path.write_text(text, encoding="utf-8")
    print(f"updated {len(files)} inventory files and {len(manifest['skill_files'])} skill hashes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
