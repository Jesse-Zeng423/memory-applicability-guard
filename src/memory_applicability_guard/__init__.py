"""Installable wrapper around the Skill helper.

The Skill package remains self-contained. This module loads that helper from a
repository checkout so `pip install -e .` can expose a CLI without copying
decision rules into a second source file.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path


def _load_helper():
    helper = Path(__file__).resolve().parents[2] / "memory-applicability-guard/scripts/guard_decision.py"
    if not helper.is_file():
        raise ImportError(
            "guard_decision.py was not found. Install this package from a clone of "
            "the repository with `pip install -e .`."
        )
    spec = importlib.util.spec_from_file_location("guard_decision", helper)
    if spec is None or spec.loader is None:
        raise ImportError(f"unable to load helper from {helper}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_HELPER = _load_helper()

BOUNDARY = _HELPER.BOUNDARY
EVIDENCE_KINDS = _HELPER.EVIDENCE_KINDS
InputValidationError = _HELPER.InputValidationError
MEMORY_ACTIONS = _HELPER.MEMORY_ACTIONS
OPTIONAL_FIELDS = _HELPER.OPTIONAL_FIELDS
PERMISSIONS = _HELPER.PERMISSIONS
RELATIONSHIPS = _HELPER.RELATIONSHIPS
REQUIRED_FIELDS = _HELPER.REQUIRED_FIELDS
RISKS = _HELPER.RISKS
__version__ = _HELPER.__version__
collect_input_errors = _HELPER.collect_input_errors
decide = _HELPER.decide
input_schema = _HELPER.input_schema
main = _HELPER.main
validate_input = _HELPER.validate_input
