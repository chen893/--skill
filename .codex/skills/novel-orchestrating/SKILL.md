---
name: novel-orchestrating
description: 长篇小说多 Skill 总控与路由：把用户需求拆解为写作/设定/大纲/摘要/线索/连续性/改稿/发布等子任务，选择并按顺序调用其他 novel-* skills；统一上下文读取顺序与权威优先级；推进每章 DoD（最小闭环）与门禁检查。用于用户请求“按系统流程推进”、不知道用哪个技能、或需要跨多个环节协同（写章+摘要+线索对账+连续性检查/大修/吃书回修）。
---

# 小说总控与路由（novel-orchestrating）

## 目标

- 把一次对话变成“可持续写到几十万字”的流程：先读对的文件、做对的步骤、把状态落盘。
- 不和其他技能抢活：只做路由、约束、门禁、推进；真正产出交给对应技能。

## 默认协议（必须遵守）

### 权威优先级（防止多真相源漂移）

- `novel/bible/**`、`novel/continuity/**`：权威事实（canon）
- `novel/decisions/decision-log.md`：变更裁决（why）
- `novel/outline/**`：计划与意图（plan）
- `novel/summaries/**`、`novel/_data/**`：派生缓存（可重建）
- `novel/draft/**`：叙事正文（可改稿，但不是权威存储）

冲突处理优先级：`bible > continuity > decisions > outline > summaries > draft`

### 默认上下文读取顺序（先小后大）

1. `novel/summaries/state.md`
2. 本任务相关的 `novel/bible/**` 与 `novel/outline/**`（尤其 scene-cards）
3. 最近章节摘要 `novel/summaries/chapters/*`
4. 仅在需要引用原句/定位冲突时，才精准回读 `novel/draft/chapters/*`

### 不确定处理（避免“编造事实”）

- 缺关键设定时：先问 1~3 个最小澄清问题。
- 用户拒绝澄清时：只做 1 个保守默认，并登记到 `novel/decisions/decision-log.md`（标注影响范围与回修计划）。
- 任何冲突：写入 `novel/continuity/issues.md`，不要悄悄改 canon 来迎合正文。

## 路由规则（用户意图 → 调用哪个 Skill）

- 写/续写/扩写章节 → `novel-chapter-drafting`（必要时先 `novel-scene-planning`）
- 总结/回顾/梳理进度 → `novel-summarizing`（更新 chapter summary + state）
- 伏笔/线索/承诺/回收安排 → `novel-thread-tracking`
- 时间线/设定一致性/逻辑查错 → `novel-continuity-checking`
- 人物卡/世界观/名词表/风格指南 → `novel-bible-managing`（重大改动同步 decision log）
- 大纲/分卷/人物弧/节奏规划 → `novel-outlining`
- 改稿/润色/结构大修 → `novel-editing`（大改后跑 continuity + summaries 闭环）
- 吃书/推翻设定/回修影响面 → `novel-retcon-managing`
- 快速定位“某事在哪章哪段” → `novel-indexing-and-searching`（先检索后打开文件）
- 发布/排版/导出稿件 → `novel-release-packaging`

## 最短路径工作流（总控执行）

1. 判定用户意图（单点任务 vs 复合任务）。
2. 选择 1~3 个要读的文件（按“默认读取顺序”，禁止一上来回读整卷/整书）。
3. 选择要调用的技能序列（最多 4 个），并说明每一步的产出文件。
4. 若涉及“写完一章”：强制检查 DoD（见下）。
5. 输出“下一步操作清单”（让作者能按清单继续，不靠记忆硬扛）。

## 每章 DoD（最小闭环，写完就做）

- 必须存在/更新：
  - `novel/draft/chapters/ch-XXX.md`
  - `novel/summaries/chapters/ch-XXX-summary.md`
  - `novel/summaries/state.md`
  - `novel/continuity/open-threads.md`（新增/回收线索对账）
- 如发现冲突/不确定：更新 `novel/continuity/issues.md`
- 如引入新设定：走 `novel-bible-managing`，并在必要时登记 `decision-log.md`

## 约束

- 不要把自己写成“万能 Skill”：总控只做调度与门禁，不输出长正文。
- 不要一次读太多：能用摘要/索引解决的，就不要回读原文。
