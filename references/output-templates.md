# 输出模板

## 咨询结论摘要

```markdown
## 考生画像
- 省份/年份：
- 科类/选科：
- 分数/位次：
- 偏好：
- 关键假设：

## 风险总览
- 冲刺：
- 稳妥：
- 保底：
- 最大风险：

## 数据来源
| 数据 | 来源 | 年份 | 状态 | 访问日期 |
|---|---|---:|---|---|
```

## 学校卡片字段

```json
{
  "name": "学校名称",
  "tier": "冲刺/稳妥/保底",
  "tags": ["985", "211", "公办"],
  "city": "城市",
  "province": "省份",
  "risk_reason": "风险说明",
  "admission_history": [
    {"year": 2025, "min_score": 0, "min_rank": 0, "plan_count": 0, "citation": "来源"}
  ],
  "recommended_majors": [
    {
      "name": "专业名称",
      "fit_reason": "推荐原因",
      "employment_outlook": "就业前景",
      "salary": {"fresh_graduate": "区间", "five_year": "区间", "citation": "来源"},
      "admission_risk": "专业录取风险"
    }
  ],
  "data_status": "官方已核验/第三方参考/需人工核验"
}
```

## HTML 骨架

```html
<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>高考志愿冲稳保报告</title>
  <style>
    body{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;margin:0;background:#f6f7fb;color:#172033}
    header{padding:32px;background:linear-gradient(135deg,#1d4ed8,#7c3aed);color:white}
    main{max-width:1180px;margin:0 auto;padding:24px}
    .grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:16px}
    .card{background:white;border-radius:16px;padding:18px;box-shadow:0 8px 24px rgba(15,23,42,.08)}
    .badge{display:inline-block;border-radius:999px;padding:4px 10px;font-size:12px;font-weight:700}
    .rush{background:#fee2e2;color:#991b1b}.safe{background:#dcfce7;color:#166534}.backup{background:#dbeafe;color:#1e40af}
    .source{font-size:12px;color:#64748b}.warn{border-left:4px solid #f59e0b;background:#fffbeb;padding:12px;border-radius:8px}
  </style>
</head>
<body>
<header><h1>高考志愿冲稳保报告</h1><p>所有录取数据以省考试院和高校招生章程为准</p></header>
<main>
  <section class="warn">本报告仅供决策辅助，不保证录取。未核验数据必须标注“需人工核验”。</section>
  <section class="grid"><!-- 学校卡片 --></section>
</main>
</body>
</html>
```
