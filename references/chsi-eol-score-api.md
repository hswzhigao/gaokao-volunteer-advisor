# 阳光高考/掌上高考专业录取分接口

## 用途

用 `scripts/fetch_gaokao_scores.py` 补充院校级录取线和专业级录取线，尤其是专业最低录取分、专业最低录取位次、专业备注、选科要求、批次和招生类型。

该数据来自阳光高考/掌上高考公开 JSON 接口。报告中标记为 `第三方参考`，最终仍需与省考试院投档线、高校招生网、正式招生计划书或高校历年录取表复核。

## 快速命令

```bash
python3 scripts/fetch_gaokao_scores.py --school-name 同济大学 --school-province 上海 --province 上海 --year 2025 --major-keyword 计算机
python3 scripts/fetch_gaokao_scores.py --school-id 73 --province 上海 --year 2025 --output tmp/tongji-shanghai-2025.json
```

## 接口分工

| 数据 | 接口 | 方法 | 用途 |
|---|---|---|---|
| 院校列表 | `https://api.eol.cn/web/api/` + `uri=apidata/api/gkv3/school/lists` | GET | 按学校名或院校所在地解析 `school_id` |
| 院校投档/录取线 | `https://api-gaokao.zjzw.cn/apidata/gh5` + `uri=v1/school/province_score` | POST JSON | 查院校/专业组最低分与位次 |
| 专业录取线 | `https://api-gaokao.zjzw.cn/apidata/gh5` + `uri=v1/school/special_score` | POST JSON | 查专业最低录取分与专业最低录取位次 |

## 关键参数

`special_score` 请求体示例：

```json
{
  "uri": "v1/school/special_score",
  "school_id": 73,
  "local_province_id": 31,
  "year": 2025,
  "type": 3,
  "page": 1,
  "size": 20,
  "platform": 1,
  "autosign": ""
}
```

- `school_id`: 院校 ID。可由院校列表接口按学校名解析。
- `local_province_id`: 生源省份，上海是 `31`。分数接口必须用 `local_province_id`，不要用 `province_id`。
- `year`: 数据年份。
- `type`: 科类编码。上海/综合改革通常用 `3`；传统文理省份需按接口返回口径复核。
- `autosign`: 匿名请求传空字符串。

## 专业字段

| 字段 | 含义 |
|---|---|
| `sp_name` | 专业名称 |
| `remark` | 专业备注、方向、培养地点等 |
| `min` | 专业最低录取分 |
| `min_section` | 专业最低录取位次 |
| `average` | 平均分，可能为 `-` |
| `sg_name` | 院校专业组代号 |
| `sg_info` | 选科要求 |
| `local_batch_name` | 批次 |
| `zslx_name` | 招生类型 |
| `lq_num` | 录取人数，可能为 `-` |
| `school_special_id` | 专业 ID |

## 使用规则

1. 先用考试院/高校官方数据建立院校或专业组候选池。
2. 对候选学校运行 `scripts/fetch_gaokao_scores.py`，补专业级 `min_score` 和 `min_rank`。
3. 在报告中把脚本结果标记为 `第三方参考`，并写明来源为 `阳光高考/掌上高考公开接口 v1/school/special_score`。
4. 如果接口返回专业分但专业组内专业、招生计划、校区、学费仍未核验，继续标注这些字段 `需人工核验`。
5. 不要用院校投档线代替专业录取线；也不要用专业级接口结果反推当年正式招生计划。

## 已知限制

- `special_score` 分页可能不稳定，`numFound` 与实际返回条数可能不一致；优先保留接口返回的原始 `raw_num_found` 方便人工判断。
- 部分学校、专业、年份可能缺数据或只返回第一页。
- 数据源不是省考试院最终投档文件，不能单独作为最终填报依据。
