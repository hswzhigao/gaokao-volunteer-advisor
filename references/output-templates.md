# 输出模板

## 咨询结论摘要

```markdown
## 考生画像
- 省份/年份：
- 科类/选科：
- 分数/位次：
- 偏好：
- 关键假设：

## 家庭画像
- 家庭预算：
- 是否支持读研：
- 是否急需本科就业：
- 是否有行业资源：
- 是否接受异地就业：
- 考公考编/体制内倾向：

## 实战派就业导向结论
- 普通家庭建议：
- 最大坑点：
- 最推荐组合：
- 最不建议组合：

## 强取舍结论
- 学校优先版：
- 专业优先版：
- 就业优先版：

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

每所学校必须有录取位次/录取排名。不能只有分数范围；若来源只给分数，显示“需补充录取排名/位次”。薪资必须区分应届生平均薪资和五年后薪资水平，且注明来源；没有来源时显示“暂无权威薪资数据，需人工核验”。**年收入/年薪在页面中不展示具体数字，使用模糊化描述（如“中等偏上”“高于行业平均”等）。**

```json
{
  "name": "学校名称",
  "tier": "冲刺/稳妥/保底",
  "school_type": "985/211/双一流/公办/民办",
  "tags": ["985", "211", "公办"],
  "city": "城市",
  "province": "省份",
  "strategy_fit": ["学校优先版", "专业优先版", "就业优先版"],
  "risk_reason": "风险说明",
  "admission_history": [
    {
      "year": 2025,
      "min_score": 0,
      "min_rank": 0,
      "admission_rank": "录取位次/录取排名",
      "plan_count": 0,
      "citation": "来源"
    }
  ],
  "school_salary": {
    "fresh_graduate_avg": "应届生平均薪资区间",
    "five_year_avg": "五年后薪资区间",
    "citation": "就业质量报告/招聘平台样本来源"
  },
  "recommended_majors": [
    {
      "name": "专业名称",
      "traffic_light": "绿灯/黄灯/红灯",
      "fit_reason": "推荐原因",
      "employment_outlook": "就业前景",
      "undergraduate_employment": "本科就业说明",
      "postgraduate_dependency": "读研依赖",
      "civil_service_fit": "考公考编适配度",
      "major_admission": {"score": "专业录取分", "rank": "专业录取位次/录取排名", "citation": "来源"},
      "salary": {
        "fresh_graduate_avg": "应届生平均薪资",
        "five_year_avg": "五年后薪资",
        "range": "页面默认展示的简短薪资范围",
        "citation": "来源和样本口径"
      },
      "admission_risk": "专业录取风险"
    }
  ],
  "data_status": "官方已核验/第三方参考/需人工核验"
}
```

## 专业红黄绿灯展示

| 专业 | 灯号 | 专业录取位次 | 本科就业 | 应届生平均薪资 | 五年后薪资水平 | 普通家庭建议 |
|---|---|---:|---|---|---|---|
| 示例专业 | 绿灯 | 18000 | 路径清晰 | 8k-12k/月 | 中等偏上 | 可优先考虑 |

专业薪资在网页中用悬浮/点击 tooltip 展示：卡片上显示简短月薪范围，`data-salary-tooltip` 中放应届生平均薪资、五年后薪资水平（模糊化描述，不展示具体年薪数字）、来源、年份、样本口径。

## HTML 骨架

```html
<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>高考志愿冲稳保报告</title>
  <style>
    *{box-sizing:border-box}
    body{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;margin:0;background:#f6f7fb;color:#172033;font-size:16px;line-height:1.6}
    header{padding:32px 20px;background:linear-gradient(135deg,#1d4ed8,#7c3aed);color:white}
    main{max-width:1180px;margin:0 auto;padding:24px}
    .filters{display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:12px;margin:16px 0}
    select,input,button{width:100%;min-height:44px;border:1px solid #cbd5e1;border-radius:12px;padding:8px 12px;font-size:16px;touch-action:manipulation;background:white}
    .grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:16px}
    .card{background:white;border-radius:16px;padding:18px;box-shadow:0 8px 24px rgba(15,23,42,.08)}
    .badge{display:inline-block;border-radius:999px;padding:4px 10px;font-size:12px;font-weight:700;margin:2px}
    .rush{background:#fee2e2;color:#991b1b}.safe{background:#dcfce7;color:#166534}.backup{background:#dbeafe;color:#1e40af}
    .green{background:#dcfce7;color:#166534}.yellow{background:#fef9c3;color:#854d0e}.red{background:#fee2e2;color:#991b1b}
    .source{font-size:12px;color:#64748b}.warn{border-left:4px solid #f59e0b;background:#fffbeb;padding:12px;border-radius:8px}
    .table-wrap{overflow-x:auto;-webkit-overflow-scrolling:touch;background:white;border-radius:16px;margin-top:16px}
    table{width:100%;border-collapse:collapse;min-width:760px}th,td{padding:10px;border-bottom:1px solid #e2e8f0;text-align:left;vertical-align:top}
    .salary-tooltip{position:relative;cursor:pointer;text-decoration:underline dotted;text-underline-offset:3px}
    .salary-tooltip:hover::after,.salary-tooltip:focus::after{content:attr(data-salary-tooltip);position:absolute;left:0;top:125%;z-index:20;width:min(320px,80vw);white-space:pre-line;background:#0f172a;color:white;border-radius:12px;padding:10px;box-shadow:0 12px 24px rgba(15,23,42,.24);font-size:13px;text-decoration:none}
    .hidden{display:none!important}
    @media (max-width: 768px){
      header{padding:24px 16px}main{padding:14px}.grid{grid-template-columns:1fr}.filters{grid-template-columns:1fr}.card{padding:14px;border-radius:14px}h1{font-size:24px}h2{font-size:20px}.badge{font-size:12px}table{font-size:14px}
    }
  </style>
</head>
<body>
<header><h1>高考志愿冲稳保报告</h1><p>就业导向、位次优先、所有录取数据以省考试院和高校招生章程为准</p></header>
<main>
  <section class="warn">本报告仅供决策辅助，不保证录取。未核验数据必须标注“需人工核验”。</section>

  <section class="card"><h2>实战派就业导向结论</h2><!-- 家庭画像 + 强取舍结论 --></section>

  <section class="filters" aria-label="筛选条件">
    <select id="tierFilter"><option value="">全部层级</option><option value="冲刺">冲刺</option><option value="稳妥">稳妥</option><option value="保底">保底</option></select>
    <select id="typeFilter"><option value="">全部类型</option><option value="985">985</option><option value="211">211</option><option value="公办">公办</option><option value="民办">民办</option></select>
    <select id="cityFilter"><option value="">全部城市</option><option value="上海">上海</option><option value="南京">南京</option></select>
    <select id="majorLightFilter"><option value="">全部专业灯号</option><option value="绿灯">绿灯</option><option value="黄灯">黄灯</option><option value="红灯">红灯</option></select>
  </section>

  <section class="grid" id="schoolGrid">
    <article class="card school-card" data-tier="稳妥" data-school-type="211 公办" data-city="南京" data-tags="211 公办 双一流" data-major-light="绿灯" data-strategy="就业优先版 专业优先版">
      <h2>示例大学 <span class="badge safe">稳妥</span></h2>
      <p>最低分：610；录取位次/录取排名：18000；招生计划：120人</p>
      <p>应届生平均薪资：<span class="salary-tooltip" tabindex="0" data-salary-tooltip="应届生平均薪资：8k-12k/月\A五年后薪资水平：中等偏上（行业参考）\A来源：就业质量报告/招聘平台样本\A说明：薪资受城市、行业和个人能力影响，年收入不单独展示">8k-12k/月</span></p>
      <p>五年后薪资水平：中等偏上</p>
      <p class="source">数据状态：需人工核验；来源：示例</p>
    </article>
  </section>

  <section class="card"><h2>专业红黄绿灯</h2><!-- 专业风险表 --></section>
</main>
<script>
  function applyFilters(){
    const tier = document.getElementById('tierFilter').value;
    const type = document.getElementById('typeFilter').value;
    const city = document.getElementById('cityFilter').value;
    const majorLight = document.getElementById('majorLightFilter').value;
    const cards = document.querySelectorAll('.school-card');
    cards.forEach(card => {
      const matchTier = !tier || card.dataset.tier === tier;
      const matchType = !type || card.dataset.schoolType.includes(type) || card.dataset.tags.includes(type);
      const matchCity = !city || card.dataset.city === city;
      const matchMajorLight = !majorLight || card.dataset.majorLight === majorLight;
      card.classList.toggle('hidden', !(matchTier && matchType && matchCity && matchMajorLight));
    });
  }
  document.querySelectorAll('.filters select').forEach(el => el.addEventListener('change', applyFilters));
  document.querySelectorAll('.salary-tooltip').forEach(el => el.addEventListener('click', () => el.focus()));
</script>
</body>
</html>
```

## 网页生成硬性要求

1. 筛选功能必须生效：不要只画 select；必须包含 `applyFilters()`、`cards.forEach`、`addEventListener('change', applyFilters)` 和每张卡片的 data 属性。
2. 手机浏览器必须适配：`viewport`、`@media (max-width: 768px)`、`.grid{grid-template-columns:1fr}`、表格 `overflow-x:auto`、控件 `min-height:44px`、`touch-action:manipulation`。
3. 薪资 tooltip 不能只依赖桌面 hover；`salary-tooltip` 必须有 `tabindex="0"` 或点击/聚焦 fallback，手机点击也能看到。
4. 学校卡片必须展示录取位次/录取排名、应届生平均薪资、五年后薪资水平（模糊化描述，不展示具体年薪）；缺数据时显示“需人工核验”，不能省略。
