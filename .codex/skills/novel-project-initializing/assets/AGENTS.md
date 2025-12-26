# 小说工作区：Codex 使用说明（skills 路由）

本仓库用于管理一个或多个小说工作区：通常位于 `projects/<书名>/novel/`，每个工作区包含 `config/ bible/ outline/ draft/ summaries/ continuity/ decisions/ reports/ _data/`。请优先使用项目内提供的 `novel-*` skills（见仓库根目录 `.codex/skills/*/SKILL.md`）来完成任务，避免临时自创流程导致“吃书/漂移/难以回溯”。

提示：若本工作区目录名不是 `novel`，运行脚本时通常需要加 `--novel-dir <本目录名>`（例如 `novel-analytics` / `novel-indexing-and-searching`）。

## 什么时候调用哪个 skill（意图 → skill）

- 不确定怎么推进 / 需要跨多个环节协同：`novel-orchestrating`
- 初始化/补齐工作区：`novel-project-initializing`
- 写/续写/扩写一章：`novel-chapter-drafting`（若缺场景卡先 `novel-scene-planning`）
- 写完一章的闭环：`novel-summarizing` → `novel-thread-tracking`（每 1~3 章可加 `novel-continuity-checking`）
- 大纲/分卷/人物弧/节奏规划：`novel-outlining`
- 场景卡/拆章/分镜/章末钩子：`novel-scene-planning`
- 设定/人物卡/地点/势力/物品/体系/风格指南：`novel-bible-managing`（名词统一补 `novel-naming-glossary-managing`）
- 吃书/设定推翻/回修影响面评估与清单：`novel-retcon-managing`
- 连续性/时间线/地理移动/能力边界查错：`novel-continuity-checking`
- 改稿/润色/结构调整：`novel-editing`（大改后建议跑 `novel-continuity-checking` + `novel-summarizing` 闭环）
- 对白与声线润色：`novel-dialogue-polishing`
- “在哪章哪段”定位/检索：`novel-indexing-and-searching`
- 字数/章长/更新进度统计：`novel-analytics`
- 发布前整理排版/导出：`novel-release-packaging`（需要平台风险自检用 `novel-sensitivity-reviewing`）

## 权威优先级（避免多真相源）

当信息冲突时，按以下优先级认定“canon”：

`bible/**`、`continuity/**` > `decisions/decision-log.md` > `outline/**` > `summaries/**`、`_data/**` > `draft/**`

- 不要为了“正文顺眼”悄悄改 canon；应走 `novel-bible-managing` / `novel-retcon-managing` 的闭环。
- `_data/**` 为索引/统计脚本生成的派生缓存，禁止手改。

## 默认读取顺序（先小后大）

1. `summaries/state.md`
2. 本任务相关 `bible/**` 与 `outline/**`（尤其 scene-cards）
3. 最近章节摘要 `summaries/chapters/*`
4. 仅在需要引用原句/定位冲突时，才精准回读 `draft/chapters/*`

## 多小说工作区选择（避免写错目录）

当仓库内存在多个小说工作区（多个 `*/novel/`）时：

- 若当前工作目录不在任何工作区内且存在多个候选，并且用户没有指定小说，我会询问一次“写哪本”，以免写错目录。

## 一句命令闭环（减少反复沟通）

当用户说“生成下一章/下一章/完成下一章”时，除非用户明确要求“只写正文”，默认执行可持续连载闭环：

1. 轻量 rehydrate：读取 `summaries/state.md` + 目标章节 scene-cards + 本章涉及的 `bible/**`（只读，避免加载整书）。
2. DoD 门禁：若发现上一章已写正文但缺少 `summaries/chapters/ch-XXX-summary.md` 或 `state.md` 未推进，先补齐摘要与状态，再写下一章。
3. 若缺场景卡：先用 `novel-scene-planning` 生成最小可写 scene-cards（1~3 张）。
4. 写正文：`draft/chapters/ch-XXX.md`（`novel-chapter-drafting`）。
5. 写完立即闭环：`novel-summarizing` → `novel-thread-tracking`（必要时登记 `continuity/issues.md` / `decisions/decision-log.md`）。

同一会话内如文件未变更，不重复整段重读；仅在检测到文件变更或跨会话重载时，才按上述最小集合 rehydrate。

## 不确定与变更登记

- 缺关键设定：先问 1~3 个最小澄清问题。
- 用户选择保守默认：登记到 `decisions/decision-log.md`（说明影响范围与回修计划）。
- 发现冲突：登记到 `continuity/issues.md`，并给最小修复策略。
