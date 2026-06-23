#!/usr/bin/env python3
"""Check that high-impact Gaokao report data carries citations."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

REQUIRED_HISTORY_FIELDS = ("year", "province", "min_score", "min_rank", "citation")
SALARY_FIELDS = ("fresh_graduate", "five_year")


def _has_text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def check_report(report: dict[str, Any]) -> dict[str, Any]:
    issues: list[str] = []
    schools = report.get("schools")
    if not isinstance(schools, list) or not schools:
        issues.append("report.schools must be a non-empty list")
        return {"valid": False, "issues": issues}

    for school_index, school in enumerate(schools):
        name = school.get("name") or f"schools[{school_index}]"
        tier = school.get("tier")
        if tier not in {"冲刺", "稳妥", "保底"}:
            issues.append(f"{name}: tier must be one of 冲刺/稳妥/保底")

        history = school.get("admission_history", [])
        if not isinstance(history, list) or not history:
            issues.append(f"{name}: admission_history must include cited score/rank records")
        else:
            for item_index, item in enumerate(history):
                for field in REQUIRED_HISTORY_FIELDS:
                    if field not in item or not _has_text(item[field]) and field == "citation":
                        issues.append(f"{name}: admission_history[{item_index}] missing required field or citation: {field}")
                if "min_score" in item and not isinstance(item["min_score"], (int, float)):
                    issues.append(f"{name}: admission_history[{item_index}].min_score must be numeric")
                if "min_rank" in item and not isinstance(item["min_rank"], int):
                    issues.append(f"{name}: admission_history[{item_index}].min_rank must be integer")

        majors = school.get("recommended_majors", [])
        if majors and not isinstance(majors, list):
            issues.append(f"{name}: recommended_majors must be a list")
            continue
        for major_index, major in enumerate(majors):
            major_name = major.get("name") or f"recommended_majors[{major_index}]"
            salary = major.get("salary")
            if isinstance(salary, dict) and any(salary.get(field) for field in SALARY_FIELDS):
                if not _has_text(salary.get("citation")):
                    issues.append(f"{name}/{major_name}: salary data requires citation")
            ranking = major.get("ranking")
            if ranking and isinstance(ranking, dict) and not _has_text(ranking.get("citation")):
                issues.append(f"{name}/{major_name}: ranking data requires citation")

    return {"valid": not issues, "issues": issues}


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("Usage: citation_check.py report.json", file=sys.stderr)
        return 2
    path = Path(argv[1])
    try:
        report = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        print(json.dumps({"valid": False, "issues": [f"failed to read JSON: {exc}"]}, ensure_ascii=False))
        return 1

    result = check_report(report)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
