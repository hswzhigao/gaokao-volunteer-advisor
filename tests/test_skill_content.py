import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class SkillContentTests(unittest.TestCase):
    def read(self, relative_path: str) -> str:
        return (ROOT / relative_path).read_text(encoding="utf-8")

    def test_skill_requires_employment_first_family_profile(self):
        skill = self.read("SKILL.md")
        required_terms = ["就业导向", "家庭画像", "普通家庭", "本科就业", "是否支持读研"]
        for term in required_terms:
            self.assertIn(term, skill)

    def test_skill_requires_major_traffic_light_and_tradeoff_outputs(self):
        skill = self.read("SKILL.md")
        required_terms = ["专业红黄绿灯", "绿灯", "黄灯", "红灯", "强取舍结论", "学校优先版", "专业优先版", "就业优先版"]
        for term in required_terms:
            self.assertIn(term, skill)

    def test_workflow_contains_realistic_family_and_career_decision_tree(self):
        workflow = self.read("references/workflow.md")
        required_terms = ["家庭与职业约束", "家庭预算", "行业资源", "考公考编", "读研依赖", "城市产业"]
        for term in required_terms:
            self.assertIn(term, workflow)

    def test_major_guide_contains_traffic_light_criteria(self):
        guide = self.read("references/major-research-guide.md")
        required_terms = ["专业红黄绿灯", "绿灯专业", "黄灯专业", "红灯风险", "普通家庭提示", "实战派"]
        for term in required_terms:
            self.assertIn(term, guide)

    def test_output_template_includes_tradeoff_and_family_fields(self):
        template = self.read("references/output-templates.md")
        required_terms = ["家庭画像", "强取舍结论", "学校优先版", "专业优先版", "就业优先版", "专业红黄绿灯"]
        for term in required_terms:
            self.assertIn(term, template)

    def test_skill_requires_rank_and_salary_not_score_only(self):
        skill = self.read("SKILL.md")
        required_terms = ["录取位次", "录取排名", "应届生平均薪资", "五年后薪资", "不能只有分数范围"]
        for term in required_terms:
            self.assertIn(term, skill)

    def test_output_template_has_working_filter_javascript(self):
        template = self.read("references/output-templates.md")
        required_terms = ["applyFilters", "addEventListener('change'", "data-tier", "data-school-type", "data-city", "data-major-light", "cards.forEach"]
        for term in required_terms:
            self.assertIn(term, template)

    def test_output_template_has_mobile_responsive_rules(self):
        template = self.read("references/output-templates.md")
        required_terms = ["@media (max-width: 768px)", "grid-template-columns:1fr", "overflow-x:auto", "min-height:44px", "touch-action:manipulation"]
        for term in required_terms:
            self.assertIn(term, template)

    def test_output_template_has_major_salary_hover_tooltip(self):
        template = self.read("references/output-templates.md")
        required_terms = ["data-salary-tooltip", "salary-tooltip", "应届生平均薪资", "五年后薪资", "悬浮"]
        for term in required_terms:
            self.assertIn(term, template)

    def test_vague_annual_salary_no_exact_figures(self):
        """年收入/年薪在页面模板中不展示具体数字，使用模糊化描述"""
        template = self.read("references/output-templates.md")
        skill = self.read("SKILL.md")
        vague_terms = ["不展示具体年薪", "模糊化描述", "中等偏上"]
        for term in vague_terms:
            self.assertIn(term, template + skill)

    def test_no_zhangxuefeng_reference(self):
        """整个 skill 不再包含张雪峰字样"""
        skill = self.read("SKILL.md")
        template = self.read("references/output-templates.md")
        workflow = self.read("references/workflow.md")
        guide = self.read("references/major-research-guide.md")
        combined = skill + template + workflow + guide
        self.assertNotIn("张雪峰", combined)

    def test_html_is_mandatory_final_output(self):
        """最终必须交付 HTML 网页，不允许只给纯文本"""
        skill = self.read("SKILL.md")
        workflow = self.read("references/workflow.md")
        required_terms = ["最终必须交付 HTML", "最终必需交付", "不允许只输出纯文本"]
        for term in required_terms:
            self.assertIn(term, skill + workflow)

    def test_schools_must_be_real_not_placeholder(self):
        """不允许用示例大学占位，HTML 中必须是具体真实院校"""
        skill = self.read("SKILL.md")
        template = self.read("references/output-templates.md")
        required_terms = ["具体真实院校", "不允许用", "占位", "真实院校"]
        for term in required_terms:
            self.assertIn(term, skill + template)

    def test_flagship_major_required(self):
        """必须标注王牌专业⭐"""
        skill = self.read("SKILL.md")
        template = self.read("references/output-templates.md")
        required_terms = ["王牌专业", "⭐", "is_flagship"]
        for term in required_terms:
            self.assertIn(term, skill + template)

    def test_per_major_admission_scores_and_ranks(self):
        """每个专业必须有独立的录取最低分和位次"""
        skill = self.read("SKILL.md")
        template = self.read("references/output-templates.md")
        required_terms = ["专业录取分", "专业录取位次", "不允许用学校投档分", "专业录取最低分"]
        for term in required_terms:
            self.assertIn(term, skill + template)

    def test_school_card_has_major_detail_table(self):
        """学校卡片内必须有专业详情表格"""
        template = self.read("references/output-templates.md")
        required_terms = ["专业</th>", "录取位次</th>", "应届生月薪</th>", "五年后水平</th>"]
        for term in required_terms:
            self.assertIn(term, template)

    def test_skill_documents_gaokao_special_score_lookup(self):
        """专业级录取分可用阳光高考/掌上高考公开接口补充"""
        skill = self.read("SKILL.md")
        data_sources = self.read("references/data-sources.md")
        api_reference = self.read("references/chsi-eol-score-api.md")
        combined = skill + data_sources + api_reference
        required_terms = [
            "scripts/fetch_gaokao_scores.py",
            "v1/school/special_score",
            "local_province_id",
            "专业最低录取分",
            "专业最低录取位次",
            "第三方参考",
        ]
        for term in required_terms:
            self.assertIn(term, combined)


if __name__ == "__main__":
    unittest.main()
