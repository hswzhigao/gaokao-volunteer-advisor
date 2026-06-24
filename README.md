# 🎓 Gaokao Volunteer Advisor

> 张雪峰式就业导向 · 高考志愿填报 AI 助手

一个面向 AI Agent（Codex / Claude Code / DimCode）的 Skill，帮助高考考生和家长以**位次优先 + 就业导向**的方式完成志愿填报分析，生成可交互的 HTML 志愿报告。

🌐 **在线样例：** [https://b23a8f15.pinme.dev/](https://b23a8f15.pinme.dev/)

---

## ✨ 核心能力

| 能力 | 说明 |
|---|---|
| **位次分析** | 以一分一段位次为核心，不是只看分数 |
| **冲稳保分类** | 根据历年录取位次自动划分冲刺/稳妥/保底院校 |
| **就业导向** | 对普通家庭本科就业、读研、考公、城市偏好等给出针对性建议 |
| **专业红黄绿灯** | 每个推荐专业标注就业前景：绿灯（本科就业OK）、黄灯（有条件）、红灯（风险大） |
| **薪资数据** | 展示应届生平均薪资 & 5年后薪资，支持网页端 hover 悬浮查看 |
| **HTML 报告** | 生成带筛选、排序、手机适配的交互式志愿报告网页 |
| **数据溯源** | 所有录取数据必须标注来源年份，缺失数据显式标注「需人工核验」 |

---

## 📦 安装

### Codex / DimCode

```bash
# 复制到 Agents skills 目录
cp -r gaokao-volunteer-advisor ~/.agents/skills/
```

### Claude Code

```bash
cp -r gaokao-volunteer-advisor ~/.claude/skills/
```

重启终端即可加载。

---

## 🚀 使用示例

在 AI 对话中直接提问即可触发 Skill：

> 「我是广东物理类考生，省排名 25000，想留在珠三角就业，
> 家庭预算有限，希望本科毕业后直接工作，
> 帮我做个志愿填报方案」

AI 会自动：
1. 收集完整家庭画像（预算、读研意愿、行业资源等）
2. 搜索广东省历年录取数据
3. 按冲/稳/保生成院校志愿表
4. 对每个专业标注红黄绿灯和薪资前景
5. 生成 HTML 交互式报告

---

## 📋 输入信息

| 字段 | 是否必需 | 说明 |
|---|---|---|
| 省份 | ✅ | 考生所在省份 |
| 年份 | ✅ | 高考年份 |
| 选科 | ✅ | 物理/历史/选科组合 |
| 分数 | ✅ | 高考总分 |
| 位次 | ✅ | 一分一段省排名 |
| 家庭画像 | ✅ | 预算、读研支持、就业紧迫度、行业资源 |
| 批次类型 | ❌ | 本科批/提前批/专项/中外合作 |
| 城市偏好 | ❌ | 意向城市 |
| 职业目标 | ❌ | 就业/读研/考公/出国 |

---

## 📂 文件结构

```
gaokao-volunteer-advisor/
├── SKILL.md                           # Skill 主文件
├── README.md                          # 本文件
├── references/
│   ├── workflow.md                    # 咨询流程
│   ├── data-sources.md                # 数据来源与搜索策略
│   ├── compliance.md                  # 合规声明与免责
│   ├── major-research-guide.md        # 专业研究方法
│   └── output-templates.md            # HTML 报告模板
├── scripts/
│   ├── validate_inputs.py             # 输入校验
│   └── citation_check.py              # 引用溯源检查
├── tests/
│   ├── test_scripts.py                # 脚本测试
│   └── test_skill_content.py          # Skill 内容合规测试
└── assets/
    └── donate-qr.jpg                  # 打赏收款码
```

---

## ⚠️ 免责声明

- 本工具为 AI 辅助分析，**不能替代**官方志愿填报系统和招生章程
- 录取数据来自公开来源，时效性和准确性需人工核实
- 薪资数据为行业平均水平，个体差异可能很大
- 最终志愿决定权在考生和家长，请务必交叉验证

---

## ☕ 打赏支持

如果这个工具帮到了你，欢迎请作者喝杯咖啡 ☕

<img src="assets/donate-qr.jpg" alt="打赏收款码" width="300" />

---

## 📄 License

MIT License — 仅供学习交流，数据准确性请自行验证。
