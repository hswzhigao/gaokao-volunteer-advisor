import importlib.util
import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"


def load_module(name: str, path: Path):
    if not path.exists():
        raise AssertionError(f"missing script: {path}")
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class ScriptTests(unittest.TestCase):
    def test_validate_inputs_accepts_complete_request(self):
        module = load_module("validate_inputs", SCRIPTS / "validate_inputs.py")
        payload = {
            "province": "河南",
            "year": 2026,
            "track": "物理类/理科",
            "score": 610,
            "rank": 18000,
            "preferences": {
                "school_tags": ["985", "211", "公办"],
                "cities": ["上海", "南京", "杭州"],
                "majors": ["计算机", "电子信息"],
            },
        }
        result = module.validate(payload)
        self.assertTrue(result["valid"])
        self.assertEqual(result["errors"], [])
        self.assertIn("2026", " ".join(result["warnings"]))

    def test_validate_inputs_rejects_missing_rank_and_invalid_score(self):
        module = load_module("validate_inputs", SCRIPTS / "validate_inputs.py")
        result = module.validate({"province": "河南", "year": 2026, "track": "理科", "score": 900})
        self.assertFalse(result["valid"])
        self.assertTrue(any("rank" in error for error in result["errors"]))
        self.assertTrue(any("score" in error for error in result["errors"]))

    def test_citation_check_fails_uncited_admission_data(self):
        module = load_module("citation_check", SCRIPTS / "citation_check.py")
        report = {
            "schools": [
                {
                    "name": "示例大学",
                    "tier": "稳妥",
                    "admission_history": [
                        {"year": 2025, "province": "河南", "min_score": 610, "min_rank": 18000}
                    ],
                    "recommended_majors": [
                        {"name": "计算机科学与技术", "salary": {"fresh_graduate": "10k-15k/月"}}
                    ],
                }
            ]
        }
        result = module.check_report(report)
        self.assertFalse(result["valid"])
        self.assertTrue(any("citation" in issue for issue in result["issues"]))

    def test_citation_check_accepts_cited_report(self):
        module = load_module("citation_check", SCRIPTS / "citation_check.py")
        report = {
            "schools": [
                {
                    "name": "示例大学",
                    "tier": "保底",
                    "admission_history": [
                        {
                            "year": 2025,
                            "province": "河南",
                            "min_score": 590,
                            "min_rank": 26000,
                            "citation": "河南省教育考试院 2025 本科批投档线，URL，访问日期 2026-06-23",
                        }
                    ],
                    "recommended_majors": [
                        {
                            "name": "电子信息工程",
                            "employment_outlook": "需求较稳定，需结合城市与个人能力判断",
                            "salary": {
                                "fresh_graduate": "8k-12k/月",
                                "five_year": "18w-35w/年",
                                "citation": "高校就业质量报告/招聘平台样本，访问日期 2026-06-23",
                            },
                        }
                    ],
                }
            ]
        }
        result = module.check_report(report)
        self.assertTrue(result["valid"])
        self.assertEqual(result["issues"], [])

    def test_validate_inputs_cli_outputs_json(self):
        script = SCRIPTS / "validate_inputs.py"
        payload = ROOT / "tests" / "tmp-input.json"
        try:
            payload.write_text(json.dumps({"province": "河南", "year": 2026, "track": "理科", "score": 610, "rank": 18000}, ensure_ascii=False), encoding="utf-8")
            completed = subprocess.run([sys.executable, str(script), str(payload)], text=True, capture_output=True)
            self.assertEqual(completed.returncode, 0, completed.stderr)
            data = json.loads(completed.stdout)
            self.assertTrue(data["valid"])
        finally:
            payload.unlink(missing_ok=True)

    def test_fetch_gaokao_scores_builds_special_score_body(self):
        module = load_module("fetch_gaokao_scores", SCRIPTS / "fetch_gaokao_scores.py")
        body = module.build_score_body("v1/school/special_score", school_id=73, local_province_id=31, year=2025, page=1, size=20)
        self.assertEqual(body["uri"], "v1/school/special_score")
        self.assertEqual(body["school_id"], 73)
        self.assertEqual(body["local_province_id"], 31)
        self.assertEqual(body["year"], 2025)
        self.assertEqual(body["page"], 1)
        self.assertEqual(body["size"], 20)
        self.assertEqual(body["autosign"], "")

    def test_fetch_gaokao_scores_normalizes_major_score_rows(self):
        module = load_module("fetch_gaokao_scores", SCRIPTS / "fetch_gaokao_scores.py")
        payload = {
            "code": 0,
            "data": {
                "item": [
                    {
                        "sp_name": "计算机科学与技术",
                        "remark": "含卓越班",
                        "min": "575",
                        "min_section": "5123",
                        "average": "578",
                        "sg_name": "（01）",
                        "sg_info": "物理+化学",
                        "local_batch_name": "本科批",
                        "zslx_name": "普通类",
                        "lq_num": "3",
                        "school_special_id": 12345,
                    }
                ]
            },
        }
        rows = module.normalize_special_scores(payload, school_name="同济大学", school_id=73, province="上海", year=2025)
        self.assertEqual(rows, [
            {
                "school_name": "同济大学",
                "school_id": 73,
                "province": "上海",
                "year": 2025,
                "major_name": "计算机科学与技术",
                "remark": "含卓越班",
                "min_score": 575,
                "min_rank": 5123,
                "average_score": 578,
                "group_name": "（01）",
                "subject_requirement": "物理+化学",
                "batch": "本科批",
                "admission_type": "普通类",
                "admission_count": "3",
                "school_special_id": 12345,
                "source": "阳光高考/掌上高考公开接口 v1/school/special_score",
                "data_status": "第三方参考，需与省考试院/高校招生网复核",
            }
        ])


if __name__ == "__main__":
    unittest.main()
