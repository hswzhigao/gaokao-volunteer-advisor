#!/usr/bin/env python3
"""Fetch school and major admission scores from public gaokao API endpoints.

The source mirrors the public JSON endpoints used by gaokao.cn / 掌上高考.
Treat returned data as third-party reference and verify against provincial
exam authorities or university admissions offices before final recommendations.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional


PROVINCES = {
    "北京": 11,
    "天津": 12,
    "河北": 13,
    "山西": 14,
    "内蒙古": 15,
    "辽宁": 21,
    "吉林": 22,
    "黑龙江": 23,
    "上海": 31,
    "江苏": 32,
    "浙江": 33,
    "安徽": 34,
    "福建": 35,
    "江西": 36,
    "山东": 37,
    "河南": 41,
    "湖北": 42,
    "湖南": 43,
    "广东": 44,
    "广西": 45,
    "海南": 46,
    "重庆": 50,
    "四川": 51,
    "贵州": 52,
    "云南": 53,
    "西藏": 54,
    "陕西": 61,
    "甘肃": 62,
    "青海": 63,
    "宁夏": 64,
    "新疆": 65,
}

LIST_URL = "https://api.eol.cn/web/api/"
SCORE_URL = "https://api-gaokao.zjzw.cn/apidata/gh5"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/131.0.0.0 Safari/537.36"
    ),
    "Referer": "https://www.gaokao.cn/",
    "Accept": "application/json, text/plain, */*",
}


def to_int(value: Any) -> Optional[int]:
    if value in (None, "", "-"):
        return None
    try:
        return int(str(value).replace(",", "").strip())
    except ValueError:
        return None


def province_id(name_or_id: str) -> int:
    if str(name_or_id).isdigit():
        return int(name_or_id)
    if name_or_id not in PROVINCES:
        raise ValueError(f"unknown province: {name_or_id}")
    return PROVINCES[name_or_id]


def request_json(url: str, method: str = "GET", params: Optional[dict] = None, body: Optional[dict] = None, retries: int = 2) -> dict:
    last_error: Optional[Exception] = None
    for attempt in range(retries + 1):
        try:
            target = url
            data = None
            headers = dict(HEADERS)
            if params:
                target = f"{url}?{urllib.parse.urlencode(params)}"
            if body is not None:
                data = json.dumps(body, ensure_ascii=False).encode("utf-8")
                headers["Content-Type"] = "application/json;charset=UTF-8"
            req = urllib.request.Request(target, data=data, headers=headers, method=method)
            with urllib.request.urlopen(req, timeout=30) as response:
                return json.loads(response.read().decode("utf-8"))
        except Exception as exc:  # noqa: BLE001
            last_error = exc
            if attempt < retries:
                time.sleep(1.0)
    raise RuntimeError(str(last_error))


def search_schools(keyword: str, school_province_id: Optional[int] = None, size: int = 30) -> List[dict]:
    params = {
        "keyword": keyword,
        "page": 1,
        "size": size,
        "uri": "apidata/api/gkv3/school/lists",
    }
    if school_province_id:
        params["province_id"] = school_province_id
    data = request_json(LIST_URL, params=params)
    if data.get("code") != "0000":
        raise RuntimeError(f"school search failed: {data.get('message') or data.get('code')}")
    return list(data.get("data", {}).get("item", []))


def resolve_school_id(school_name: str, school_province_id: Optional[int] = None) -> dict:
    schools = search_schools(school_name, school_province_id=school_province_id)
    exact = [school for school in schools if school.get("name") == school_name]
    if exact:
        return exact[0]
    if len(schools) == 1:
        return schools[0]
    names = ", ".join(str(s.get("name")) for s in schools[:10])
    raise RuntimeError(f"could not resolve unique school for {school_name}; candidates: {names}")


def build_score_body(uri: str, school_id: int, local_province_id: int, year: int, score_type: int = 3, page: Optional[int] = None, size: Optional[int] = None) -> dict:
    body = {
        "uri": uri,
        "school_id": school_id,
        "local_province_id": local_province_id,
        "year": year,
        "type": score_type,
        "platform": 1,
        "autosign": "",
    }
    if page is not None:
        body["page"] = page
    if size is not None:
        body["size"] = size
    return body


def fetch_province_score(school_id: int, local_province_id: int, year: int, score_type: int = 3) -> dict:
    body = build_score_body("v1/school/province_score", school_id, local_province_id, year, score_type=score_type)
    return request_json(SCORE_URL, method="POST", body=body)


def fetch_special_score(school_id: int, local_province_id: int, year: int, score_type: int = 3, page: int = 1, size: int = 20) -> dict:
    body = build_score_body("v1/school/special_score", school_id, local_province_id, year, score_type=score_type, page=page, size=size)
    return request_json(SCORE_URL, method="POST", body=body)


def normalize_province_scores(payload: dict, school_name: str, school_id: int, province: str, year: int) -> List[dict]:
    rows = []
    for item in payload.get("data", {}).get("item", []):
        rows.append(
            {
                "school_name": item.get("name") or school_name,
                "school_id": item.get("school_id") or school_id,
                "province": item.get("local_province_name") or province,
                "year": item.get("year") or year,
                "group_name": item.get("sg_name"),
                "subject_requirement": item.get("sg_info"),
                "special_group": item.get("special_group"),
                "min_score": to_int(item.get("min")),
                "min_rank": to_int(item.get("min_section")),
                "batch": item.get("local_batch_name"),
                "admission_type": item.get("zslx_name"),
                "admission_count": item.get("num"),
                "source": "阳光高考/掌上高考公开接口 v1/school/province_score",
                "data_status": "第三方参考，需与省考试院/高校招生网复核",
            }
        )
    return rows


def normalize_special_scores(payload: dict, school_name: str, school_id: int, province: str, year: int) -> List[dict]:
    rows = []
    for item in payload.get("data", {}).get("item", []):
        rows.append(
            {
                "school_name": school_name,
                "school_id": school_id,
                "province": province,
                "year": year,
                "major_name": item.get("sp_name"),
                "remark": item.get("remark"),
                "min_score": to_int(item.get("min")),
                "min_rank": to_int(item.get("min_section")),
                "average_score": to_int(item.get("average")),
                "group_name": item.get("sg_name"),
                "subject_requirement": item.get("sg_info"),
                "batch": item.get("local_batch_name"),
                "admission_type": item.get("zslx_name"),
                "admission_count": item.get("lq_num"),
                "school_special_id": item.get("school_special_id"),
                "source": "阳光高考/掌上高考公开接口 v1/school/special_score",
                "data_status": "第三方参考，需与省考试院/高校招生网复核",
            }
        )
    return rows


def filter_majors(rows: Iterable[dict], keywords: Iterable[str]) -> List[dict]:
    words = [word for word in keywords if word]
    if not words:
        return list(rows)
    return [
        row
        for row in rows
        if any(word in str(row.get("major_name") or "") or word in str(row.get("remark") or "") for word in words)
    ]


def run(args: argparse.Namespace) -> dict:
    local_pid = province_id(args.province)
    school = {"school_id": args.school_id, "name": args.school_name or str(args.school_id)}
    if not args.school_id:
        school_loc_pid = province_id(args.school_province) if args.school_province else None
        school = resolve_school_id(args.school_name, school_province_id=school_loc_pid)
    sid = int(school["school_id"])
    school_name = str(school.get("name") or args.school_name or sid)

    province_payload = fetch_province_score(sid, local_pid, args.year, score_type=args.score_type)
    if not args.school_name:
        first_school_name = next(
            (item.get("name") for item in province_payload.get("data", {}).get("item", []) if item.get("name")),
            None,
        )
        if first_school_name:
            school_name = str(first_school_name)
            school["name"] = school_name
    special_payload = fetch_special_score(sid, local_pid, args.year, score_type=args.score_type, size=args.size)
    province_rows = normalize_province_scores(province_payload, school_name, sid, args.province, args.year)
    special_rows = normalize_special_scores(special_payload, school_name, sid, args.province, args.year)
    special_rows = filter_majors(special_rows, args.major_keyword or [])
    return {
        "school": school,
        "province": args.province,
        "year": args.year,
        "province_scores": province_rows,
        "special_scores": special_rows,
        "raw_num_found": {
            "province_score": province_payload.get("data", {}).get("numFound"),
            "special_score": special_payload.get("data", {}).get("numFound"),
        },
        "data_status": "第三方参考，最终以省考试院、招生计划书和高校招生网为准",
    }


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Fetch gaokao school and major admission scores.")
    school = parser.add_mutually_exclusive_group(required=True)
    school.add_argument("--school-id", type=int)
    school.add_argument("--school-name")
    parser.add_argument("--province", required=True, help="生源省份名称或ID，如 上海 或 31")
    parser.add_argument("--school-province", help="院校所在地省份名称或ID，用于同名学校消歧")
    parser.add_argument("--year", required=True, type=int)
    parser.add_argument("--score-type", type=int, default=3, help="科类编码；上海/综合改革通常用 3")
    parser.add_argument("--major-keyword", action="append", help="按专业名或备注关键词过滤，可重复")
    parser.add_argument("--size", type=int, default=20, help="special_score 请求 size；接口实际返回数量可能小于 size")
    parser.add_argument("--output", type=Path)
    return parser.parse_args(argv)


def main(argv: Optional[List[str]] = None) -> int:
    args = parse_args(argv)
    result = run(args)
    text = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text + "\n", encoding="utf-8")
    else:
        print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
