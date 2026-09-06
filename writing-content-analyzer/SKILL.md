---
name: writing-content-analyzer
description: >-
  解析文章、访谈转录、会议记录、网页摘录、PDF/DOCX 文本和多文件素材，提炼可追溯的事实、观点、金句、对话动态、时间线、人物关系、证据缺口与可写角度，输出 content-analysis.md 与 content-analysis.json。用于写作前的素材盘点、长素材压缩、采访稿整理、系列内容建库和为 outline-generator/writer 提供可靠输入；严禁把推断写成事实。
---

# 写作素材分析

先建立“事实底座”，再讨论文章怎么写。所有重要结论都要能回指原始素材，无法确认的内容必须显式标记。

## 输入检查

先建立六格需求卡，并检查：

- 是否能读取输入文件；记录文件名、类型、日期和来源。
- 是否存在 OCR 错字、说话人缺失、截断、重复、乱码或表格未展开。
- 是否指定目标读者、文章目的、平台、时效性和禁止披露的信息。
- 是否需要保留原话；若需要，原话必须带来源锚点。

输入过长时按文件或语义段分批处理，最后做一次跨批次去重和一致性合并。不要只根据摘要写分析。

## 工作流程

1. 建立来源登记表，为每个文件和段落分配稳定的 `S01`, `S02`…编号；引用原文时使用 `[S01:p12]`、`[S02:00:14:32]` 等锚点，无法定位时说明原因。
2. 提取事实、数字、时间、人物、机构、产品名、事件和原话。给每条内容标注 `confirmed`、`reported`、`inferred` 或 `needs-check`。
3. 提取文章主旨候选、关键论点、论据、反例、冲突观点、情绪变化、对话动态和可复用的内容块；区分“素材原意”和“适合写作的表达”。
4. 识别缺口与风险：缺少来源、时间不一致、数字口径不一致、可能涉及隐私/版权/敏感信息、未经证实的因果关系、可能被误解的表述。
5. 形成 2–5 个写作角度，每个角度写清目标读者、核心承诺、可用证据、缺口和不适合使用的材料。
6. 输出 `content-analysis.md` 与 `content-analysis.json`，并在末尾列出“写作前必须人工确认”的事项。

## 产物契约

`content-analysis.md` 至少包含：

1. 来源登记与质量说明
2. 一句话主旨候选与文章目的
3. 事实清单（含状态和来源锚点）
4. 金句/原话清单（保持原文，单独标注是否可公开）
5. 人物、事件、时间线与关系
6. 论点—证据矩阵、冲突与证据缺口
7. 可写角度、素材取舍建议与风险提示
8. 禁止推断和待确认清单

`content-analysis.json` 建议遵循以下最小结构：

```json
{
  "version": "1.0",
  "sources": [{"id": "S01", "name": "", "type": "", "locator_notes": ""}],
  "brief": {"purpose": "", "audience": "", "platform": "", "time_sensitivity": ""},
  "thesis_candidates": [],
  "facts": [{"id": "F01", "statement": "", "status": "confirmed", "source_ids": [], "risk": ""}],
  "quotes": [{"id": "Q01", "text": "", "speaker": "", "source_ids": [], "public_use": "unknown"}],
  "entities": [],
  "timeline": [],
  "claims": [{"id": "C01", "claim": "", "evidence_ids": [], "counterpoints": []}],
  "content_blocks": [],
  "angles": [],
  "gaps": [],
  "risk_flags": [],
  "do_not_infer": []
}
```

下游 Skill 只可直接使用 `confirmed` 和明确标为 `reported` 的内容；`inferred` 只能作为待验证假设，`needs-check` 不得写成确定性表述。

## 质量门禁

- [ ] 每个关键数字、原话和结论都有来源锚点。
- [ ] 已分离事实、观点、推断和建议。
- [ ] 已处理重复素材、相互矛盾的说法和不完整片段。
- [ ] 没有因为“读起来合理”而补写素材中不存在的事实。
- [ ] 已标出隐私、版权、保密和敏感信息风险。

## 参考

需要字段、状态值和来源锚点的详细定义时，读取 `references/analysis-schema.md`。
