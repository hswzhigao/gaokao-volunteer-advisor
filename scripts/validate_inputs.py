#!/usr/bin/env python3
"""Validate structured Gaokao volunteer-advisor input JSON."""

from __future__ import annotations

import json
import sys
from datetime import date
from pathlib import Path
from typing import Any

VALID_PROVINCES = {
    "北京", "天津", "河北", "山西", "内蒙古", "辽宁", "吉林", "黑龙江", "上海", "江苏", "浙江", "安徽",
    "福建", "江西", "山东", "河南", "湖北", "湖南", "广东", "广西", "海南", "重庆", "四川", "贵州",
    "云南", "西藏", "陕西", "甘肃", "青海", "宁夏", "新疆", "香港", "澳门", "台湾"
}


def _present(value: Any) -> bool:
    return value is not None and value != "" and value != [] and value != {}


def validate(payload: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []

    province = payload.get("province")
    year = payload.get("year")
    track = payload.get("track")
    score = payload.get("score")
    rank = payload.get("rank")

    for field, value in (
        ("province", province),
        ("year", year),
        ("track", track),
        ("score", score),
        ("rank", rank),
    ):
        if not _present(value):
            errors.append(f"missing required field: {field}")

    if _present(province) and province not in VALID_PROVINCES:
        warnings.append(f"province '{province}' is not in the built-in province list; verify spelling and policy scope")

    current_year = date.today().year
    if _present(year):
        if not isinstance(year, int):
            errors.append("year must be an integer")
        elif year < 2020 or year > current_year + 2:
            warnings.append(f"year {year} is outside the normal recent Gaokao data window; verify policy/data availability")
        elif year >= current_year:
            warnings.append(f"year {year} may depend on current-year official plans, 一分一段表, and admissions rules")

    if _present(score):
        if not isinstance(score, (int, float)):
            errors.append("score must be a number")
        elif score < 0 or score > 750:
            errors.append("score must be between 0 and 750 unless a province-specific full score is explicitly documented")

    if _present(rank):
        if not isinstance(rank, int):
            errors.append("rank must be an integer")
        elif rank <= 0:
            errors.append("rank must be a positive integer")

    if _present(track) and not isinstance(track, str):
        errors.append("track must be a string such as 文科/理科/历史类/物理类/选科组合")

    prefs = payload.get("preferences", {})
    if prefs and not isinstance(prefs, dict):
        errors.append("preferences must be an object when provided")

    return {"valid": not errors, "errors": errors, "warnings": warnings}


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("Usage: validate_inputs.py input.json", file=sys.stderr)
        return 2
    path = Path(argv[1])
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001 - CLI should surface readable errors
        print(json.dumps({"valid": False, "errors": [f"failed to read JSON: {exc}"], "warnings": []}, ensure_ascii=False))
        return 1

    result = validate(payload)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
