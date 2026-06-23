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


if __name__ == "__main__":
    unittest.main()
