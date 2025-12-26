---
name: novel-editing
description: 改稿与润色：对章节草稿做结构修订、节奏与情绪曲线调整、语言润色与对白优化，并在改动后触发连续性复检与摘要闭环。用于“润色/二稿/大修、删改合并场景、提升节奏与爽点密度、修复连续性报告里的 P0/P1 问题”等需求。
---

# 改稿与润色（novel-editing）

## 目标

- 把“能看”改成“能追更”：结构清晰、节奏在线、信息增量稳定。
- 改稿必须闭环：正文变了，摘要/线索/时间线也要跟着变。

## 输入（按需）

- 目标章节：`novel/draft/chapters/ch-*.md`
- 风格约束：`novel/bible/style-guide.md`
- 连续性报告：`novel/reports/continuity/report-*.md`（若有）
- state/摘要（用于避免改完自己忘了改哪儿）

## 最短路径工作流

1. 选择改稿层级：
   - 结构层：删/并/移场景，修因果链
   - 节奏层：信息增量、冲突升级、代价与爽点
   - 文笔层：句式、意象、视角贴合、对白声线
2. 改正文（尽量最小改动修复 P0）。
3. 输出改稿记录（可选但推荐）：`novel/reports/editing/edit-pass-*.md`
4. 改完强制闭环：
   - 触发 `novel-summarizing` 更新摘要/state
   - 触发 `novel-thread-tracking` 对账线索
   - 必要时再跑 `novel-continuity-checking`

## 输出要求（必须落盘）

- 改动后的章节文件（或章节范围）
- 如影响剧情事实：提醒更新摘要/线索/时间线（不要只改正文）

## 模板（可选）

如需改稿记录模板，复制 `assets/edit-pass-template.md`。

