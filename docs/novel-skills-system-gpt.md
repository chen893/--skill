# 长篇小说多 Skill 系统设计（GPT）

本设计文档面向“数十万字长篇小说”的**创作 + 管理**场景，目标是把小说写作拆解为一组可组合的 Skills（单一职责、可渐进加载、可脚本化），在不把整部小说塞进上下文的前提下，仍能长期保持一致性、推进节奏、可追溯修改。

参考：本仓库 `skills.md` 与 `skills最佳实践.md`（技能三层加载、命名/描述/渐进式披露/工作流与反馈循环等约束与模式）。

---

## 1. 设计目标（针对“长篇”痛点）

- **可扩展上下文**：章节越来越多时，仍能靠结构化“小说知识库”与分层摘要持续写下去。
- **一致性与连续性**：人物、时间线、设定、伏笔与已埋线索可被检查、追踪、回收。
- **可管理的复杂度**：把“灵感/设定/大纲/场景/草稿/修订/校对/发布”分离，避免一个万能技能变成不可维护的提示墙。
- **可复用流程**：把重复性工作（索引、摘要更新、连续性检查、导出）变成稳定的工作流/脚本。
- **可审计与可回滚**：重要设定/改动有决策记录与影响评估，降低“改一处崩全书”风险。

---

## 2. 关键原则（把最佳实践落到小说场景）

### 2.1 Skill 颗粒度与职责边界

- 每个 Skill **单一职责**：只解决一个稳定问题（例如“连续性检查”），不要“写作 + 大纲 + 修订 + 排版”全塞一个 Skill。
- 允许一个“总控/路由”Skill，但它只做**分流、调度、状态推进**，不吞并其他技能职责。

### 2.2 发现机制：描述字段要“可触发”

遵循 `skills最佳实践.md`：`description` 用第三人称写清“做什么 + 何时使用”，并嵌入关键词（中文 + 英文/缩写）以提高命中率。

### 2.3 渐进式披露（Progressive Disclosure）

遵循 `skills.md` 三层加载模型：

- **Level 1（始终加载）**：只靠 `name + description` 让系统知道“有什么、何时用”。
- **Level 2（触发时加载）**：SKILL.md 只放“最短路径工作流 + 导航”；尽量 < 500 行。
- **Level 3（按需）**：把模板、清单、参考资料、脚本拆到 `assets/`、`references/`、`scripts/`，需要时再读/执行。

并遵循“避免深层嵌套引用”：所有关键参考文件尽量从 SKILL.md **一级直链**。

### 2.4 统一“小说数据模型”（跨 Skill 协作的地基）

多 Skill 能协作的前提是：**共享同一套实体、ID、文件约定、更新协议**。否则会出现“每个 Skill 都在写自己的平行宇宙设定集”。

---

## 3. 小说工作区（作品本体）的推荐目录结构

> Skills 是工具箱；作品数据要落在稳定的“小说工作区”。下方结构可在任何仓库/目录中使用。

```
novel/
  README.md
  config/
    novel.yaml                # 体裁、视角、时态、禁忌、字数目标、卷章结构等
  bible/                      # 小说圣经：权威设定（Source of Truth）
    characters/
      char-*.md
    locations/
      loc-*.md
    factions/
      fac-*.md
    items/
      item-*.md
    systems/
      sys-*.md                # 魔法/科技/规则系统
    glossary.md               # 专有名词表
    style-guide.md            # 叙事口吻/用词/标点/敏感点/人称时态等
  outline/
    master-outline.md         # 总大纲（含主线/支线/主题/终局）
    arcs/
      arc-*.md                # 单条故事线（人物弧/案件弧/情感弧）
    scene-cards/
      scn-*.md                # 场景卡（建议：一场景一文件）
  draft/
    chapters/
      ch-001.md
      ch-002.md
  summaries/                  # 分层摘要：为“长篇”节省上下文
    state.md                  # 当前故事状态（1~2 页，持续维护）
    chapters/
      ch-001-summary.md
      ch-002-summary.md
    volumes/
      vol-01-summary.md
  continuity/
    timeline.md               # 事件时间线（按日期/相对时间）
    open-threads.md           # 未收束线索/承诺（promise-payoff）
    constraints.md            # 不可违反的硬约束（年龄/地理/规则）
    issues.md                 # 已知连续性风险与待修
  decisions/
    decision-log.md           # 重大设定/改动的决策记录（含影响范围）
  research/
    sources/                  # 离线资料/剪贴/引用（避免依赖在线）
    notes.md
  reports/
    continuity/
      report-YYYYMMDD.md
    editing/
      edit-pass-*.md
```

**为什么要有 `novel/summaries/state.md`：**当章节累计到几十万字，写下一章时不应该反复读全书；应优先读 `novel/summaries/state.md` + 相关人物/地点/上一章摘要，必要时再精准回读某章段落。

---

## 4. 共享约定（所有 Skills 必须遵守）

### 4.1 ID 体系（稳定引用，避免重名混乱）

建议前缀：

- `char-` 人物、`loc-` 地点、`fac-` 势力、`item-` 物件、`sys-` 规则系统
- `arc-` 故事弧、`scn-` 场景、`ch-` 章节、`evt-` 事件、`thr-` 线索/承诺

ID 使用小写字母/数字/连字符，尽量不含中文，便于跨平台与脚本处理。

### 4.2 实体文件的最小 Frontmatter（可选但强烈建议）

人物示例（`novel/bible/characters/char-lin-yu.md`）：

```yaml
---
id: char-lin-yu
name: 林雨
role: protagonist
pov: true
first_appearance: ch-001
tags: [学生, 黑客]
relationships:
  - target: char-chen-mo
    type: 盟友
---
```

### 4.3 写作输出与“知识库更新”必须解耦

- **草稿写作**只改 `novel/draft/chapters/`。
- **权威事实**只落 `novel/bible/` 与 `novel/continuity/`。
- 任何新增/变更设定，必须同步更新：`novel/bible/` + `novel/decisions/decision-log.md`（如果是重大改动）。

### 4.4 章节交付的“Definition of Done”（最小闭环）

每完成一章（或一次大修）至少更新：

- `novel/draft/chapters/ch-XXX.md`
- `novel/summaries/chapters/ch-XXX-summary.md`
- `novel/summaries/state.md`（推进当前状态）
- `novel/continuity/open-threads.md`（新增/回收线索）

---

## 5. Skill 系统分层（建议 1 总控 + 8 核心 + N 可选）

> 下方是“技能地图”。实现时每个技能各自一个目录：`<skill-name>/SKILL.md`，并按需带 `references/ assets/ scripts/`。

### 5.1 总控（Router / Operating Skill）

#### `novel-orchestrating`

**定位**：把用户请求映射到正确的工作流与文件读写范围；控制“读什么、不读什么”；把长篇任务拆为可迭代的短回合。

**建议描述（示例）**：

```yaml
---
name: novel-orchestrating
description: 协调长篇小说项目的写作与管理：选择合适的工作流、最小化读取范围、维护 state/summary/thread/timeline 的更新节奏。当用户提出小说项目总体推进、跨章节一致性、流程编排、或不确定该怎么开始/下一步做什么时使用。
---
```

### 5.2 核心写作链路（从计划到草稿）

#### `novel-project-initializing`
- 做什么：初始化 `novel/` 目录、生成 `config/novel.yaml`、空白模板、索引入口（README、state）。
- 触发词：初始化、建项目、目录结构、从零开始、开坑。

#### `novel-bible-managing`
- 做什么：创建/维护小说圣经（人物/地点/势力/系统/名词表/风格指南），保证“权威事实”唯一来源。
- 触发词：设定、人物表、世界观、名词、规则、风格指南、统一设定。

#### `novel-outlining`
- 做什么：产出总大纲、分卷分章、情节节点（beats）、因果链；把主题与终局落到可执行结构。
- 触发词：大纲、分章、三幕、节拍表、剧情推进、结构。

#### `novel-scene-planning`
- 做什么：把“章”拆成场景卡（scn），明确 POV/地点/时间/目标-冲突-结果/信息揭示/线索。
- 触发词：场景卡、分镜、这一章怎么写、冲突、节奏。

#### `novel-chapter-drafting`
- 做什么：根据场景卡与约束写章节草稿；严格遵循 `style-guide.md` 与 POV/时间线。
- 触发词：写一章、写第 X 章、扩写、续写、正文、对白、描写。

### 5.3 长篇必备的“记忆与一致性”链路

#### `novel-summarizing`
- 做什么：生成并维护分层摘要（章摘要/卷摘要/state），确保后续写作不必回读全书。
- 触发词：总结、摘要、state 更新、上一章回顾、梳理。

#### `novel-thread-tracking`
- 做什么：维护 `open-threads.md`：承诺/伏笔/悬念/未解决问题的清单，记录“何时埋、何时收”。
- 触发词：伏笔、线索、回收、坑、悬念、promise-payoff。

#### `novel-continuity-checking`
- 做什么：连续性检查（人物年龄/时间线/地理距离/规则一致性/出场缺失），输出报告并登记 issues。
- 触发词：连续性、时间线冲突、设定冲突、查错、核对、复盘。

### 5.4 修订与交付链路

#### `novel-editing`
- 做什么：按“修订轮次”处理（结构修/节奏修/情绪曲线/语句与标点），并把改动影响写入 `edit-pass` 报告。
- 触发词：润色、改写、二稿、三稿、去水、增强张力、统一口吻。

#### `novel-release-packaging`（可选）
- 做什么：把章节合并为交付稿（Markdown/Docx/PDF 等）；生成目录、卷章标题、统一格式。
- 触发词：导出、排版、成稿、投稿版、EPUB/PDF/DOCX。

---

## 6. 跨 Skill 协作协议（“谁读什么、谁改什么”）

为避免重复劳动与互相覆盖，强制约定每类任务的最小读写集合：

- **写正文**（`novel-chapter-drafting`）：
  - 读：`novel/summaries/state.md`、相关 `novel/bible/*`、相关 `novel/outline/scene-cards/*`、上一章摘要
  - 写：`novel/draft/chapters/ch-XXX.md`
  - 不直接写：`novel/bible/`、`novel/continuity/timeline.md`（交给后续技能）

- **写完一章后收尾**（`novel-summarizing` + `novel-thread-tracking`）：
  - 读：本章草稿、上一版 state/thread
  - 写：章摘要、更新 state、更新 open-threads（新增/回收）

- **一致性 QA**（`novel-continuity-checking`）：
  - 读：`novel/summaries/state.md`、`novel/continuity/timeline.md`、相关人物/地点卡、目标章节（必要时）
  - 写：`novel/reports/continuity/report-*.md`、更新 `novel/continuity/issues.md`、必要时更新 `novel/continuity/timeline.md`

- **改设定/大改动**（`novel-bible-managing`）：
  - 写：`novel/bible/*`、`novel/decisions/decision-log.md`
  - 同步：在 `novel/continuity/issues.md` 中登记“需要回修的章节范围”（避免遗漏）

---

## 7. 关键模板（建议放入各 Skill 的 assets/，此处先定义标准）

### 7.1 场景卡模板（`novel/outline/scene-cards/scn-*.md`）

```markdown
---
id: scn-0001
chapter: ch-001
time: D+3 21:00
location: loc-old-town
pov: char-lin-yu
threads_open: [thr-0007]
threads_close: []
---

# 场景卡：一句话概述

## 目标（Goal）

## 冲突（Conflict）

## 结果（Outcome）

## 关键动作与节拍（Beats）
- ...

## 信息揭示 / 伏笔
- ...

## 连续性约束（必须满足）
- ...
```

### 7.2 章节摘要模板（`novel/summaries/chapters/ch-XXX-summary.md`）

```markdown
# ch-XXX 摘要

## 本章发生了什么（5~10 条要点）
- ...

## 人物状态变化（按人物 ID）
- char-...：...

## 新增/更新设定（如有，指向 bible 文件）
- ...

## 开启的线索（threads_open）
- thr-...：一句话 + 预计回收窗口

## 回收的线索（threads_close）
- thr-...：如何回收
```

### 7.3 `novel/summaries/state.md`（长期维护的“当前态”）

```markdown
# 当前故事状态（state）

## 故事进度
- 已完成：ch-001 ~ ch-XXX
- 当前时间线：D+?
- 当前地点：loc-...
- 当前 POV：char-...

## 主线现状（1 段）

## 关键人物现状（每人 1~2 句）
- char-...：...

## 关键约束（不可违反）
- ...

## 近期写作目标（接下来 1~3 章）
- ...
```

### 7.4 连续性报告模板（`novel/reports/continuity/report-*.md`）

```markdown
# 连续性检查报告（YYYY-MM-DD）

## 检查范围
- 章节：ch-...
- 参考：timeline、bible（列出关键文件）

## 发现的问题（按严重度）
### P0（必须修）
- ...

### P1（建议修）
- ...

### P2（记录即可）
- ...

## 建议的修复策略
- 最小改动方案：...
- 如需改设定：需要更新哪些 bible 文件、影响哪些章节
```

### 7.5 线索清单模板（`novel/continuity/open-threads.md`）

```markdown
# 未收束线索 / 承诺清单（open threads）

> 目标：把“作者对读者做出的承诺”显式化，避免遗忘、烂尾或提前泄底。

| thread_id | 标题 | 类型 | 首次出现 | 当前状态 | 预计回收窗口 | 依赖 | 回收章节 | 备注 |
|---|---|---|---|---|---|---|---|---|
| thr-0007 | ... | 伏笔/悬念/承诺/谜题/情感弧 | ch-012 | open | ch-020~ch-030 | char-.../evt-... |  | ... |

## 维护规则
- 新线索：写入表格，并在对应 `novel/summaries/chapters/ch-XXX-summary.md` 的 threads_open 里登记
- 回收线索：补全“回收章节”，把状态改为 closed，并在对应摘要的 threads_close 里登记
- 不确定：保留 open，但在备注中写 TODO，并同步到 `novel/continuity/issues.md`
```

### 7.6 时间线模板（`novel/continuity/timeline.md`）

```markdown
# 时间线（timeline）

> 目标：保证“先后顺序、时间跨度、地理移动、年龄/季节/昼夜”在长篇里不漂移。

## 时间基准
- Day 0：...
- 计时方式：D+N（相对天数）/ 具体日期（可选）

## 事件表

| event_id | 时间 | 地点 | 参与者 | 关联章节 | 一句话 | 约束/校验点 |
|---|---|---|---|---|---|---|
| evt-0001 | D+3 21:00 | loc-old-town | char-lin-yu | ch-001 | ... | 距离/交通/目击者/天气 |
```

### 7.7 决策记录模板（`novel/decisions/decision-log.md`）

```markdown
# 决策记录（decision log）

> 目标：把重大设定/剧情改动的“原因与代价”写清楚，避免反复推翻或隐性蝴蝶效应。

| decision_id | 日期 | 决策 | 原因 | 替代方案 | 影响范围 | 回修清单 | 状态 |
|---|---|---|---|---|---|---|---|
| dec-20251225-01 | 2025-12-25 | ... | ... | ... | ch-010~ch-030、char-...、sys-... | [ ] ch-012 [ ] ch-018 | planned/in-progress/done |

## 规则
- 任何“会影响既有章节或设定一致性”的改动都必须登记
- 影响范围必须可定位：章节范围 + 实体 ID（char/loc/sys/thr/evt）
```

---

## 8. 推荐工作流（把长篇拆成短回合迭代）

### 8.1 从 0 到 1：开坑工作流

1. `novel-project-initializing`：生成目录与基础模板（config、style-guide、state、decision-log）。
2. `novel-bible-managing`：先写“硬约束”（世界规则、时间线基准、人物核心动机）。
3. `novel-outlining`：产出 `master-outline.md`（主线 + 终局 + 主题承诺）。
4. `novel-scene-planning`：把第 1 卷/前 3 章拆成场景卡。
5. 循环进入“写章工作流”。

### 8.2 写一章：最小闭环工作流（建议每章固定执行）

1. `novel-chapter-drafting`：只读 `novel/summaries/state.md` + 相关 `novel/bible/*` + 本章场景卡 → 写草稿。
2. `novel-summarizing`：写 `novel/summaries/chapters/ch-XXX-summary.md` + 更新 `novel/summaries/state.md`。
3. `novel-thread-tracking`：更新 `novel/continuity/open-threads.md`（新增/回收线索）。
4. `novel-continuity-checking`（可每 1~3 章一次）：输出 `novel/reports/continuity/report-*.md` + 更新 `novel/continuity/issues.md`。

### 8.3 大修：结构修订工作流

1. `novel-editing`：先做结构层（删/并/移场景），再做节奏与情绪曲线，最后行文润色。
2. `novel-continuity-checking`：确认时间线与设定一致。
3. `novel-summarizing`：更新卷摘要与 state（防止“旧摘要误导后续写作”）。
4. 如涉及设定改动：`novel-bible-managing` + 更新 `novel/decisions/decision-log.md`。

### 8.4 设定变更 / Retcon：安全修改工作流

1. 先写入 `novel/decisions/decision-log.md`：说明“为何改、替代方案、影响范围、回修清单”。
2. `novel-bible-managing`：更新 `novel/bible/**`，把新设定落为权威事实。
3. `novel-continuity-checking`：对影响章节范围出报告（至少列 P0 必修点）。
4. `novel-editing`：按回修清单逐章修正文（避免在正文里留下旧设定残影）。
5. `novel-summarizing`：更新受影响章节摘要 + state +（必要时）卷摘要。
6. `novel-thread-tracking`：检查线索表是否需要重排“回收窗口”。

---

## 9. 可选扩展技能（按需要逐步添加）

- `novel-analytics`：统计字数、章长分布、POV 占比、角色出场频次（适合脚本化）。
- `novel-dialogue-polishing`：对白风格与角色声线一致性（与 `style-guide` 强绑定）。
- `novel-sensitivity-reviewing`：敏感内容与风险点清单化审查（合规/平台规范）。
- `novel-naming-glossary-managing`：专名一致性（地名、人名、组织名、译名）。
- `novel-retcon-managing`：对“设定变更/回修”做影响评估、生成回修清单、推进闭环（与 8.4 配套）。
- `novel-indexing-and-searching`：生成/维护实体索引与快速检索入口（当角色/地点/事件数量很大时使用）。

---

## 10. 落地实现建议（把本设计转成真正的 Skill 套件）

1. 每个技能一个目录：`novel-*/SKILL.md`，并按需配 `assets/ references/ scripts/`。
2. SKILL.md 只放“最短路径流程 + 导航链接”，把模板/清单放 `assets/`，把资料放 `references/`。
3. 所有路径使用**相对路径**（优先 POSIX 风格），避免平台绑定。
4. 在每个 Skill 的 `description` 中写清触发词，减少技能冲突与误触发。
5. 先实现最小核心链路（初始化/圣经/大纲/写章/摘要/线索/连续性/修订），写够 3~5 章再迭代补齐扩展技能。

---

## 11. 总控 Skill 的“系统协议”（建议写进 `novel-orchestrating`）

把下面当作“长篇小说的系统提示”，用于约束 GPT 的行为，让多 Skill 在长周期里稳定工作。

### 11.1 默认上下文选择（先小后大）

1. **永远优先读**：`novel/summaries/state.md`
2. 再读：相关 `novel/bible/**`（人物/地点/规则）与本章 `novel/outline/scene-cards/**`
3. 再读：上一章/相关章的 `novel/summaries/chapters/**`
4. **最后才回读正文**：仅在发现冲突或需要复用具体段落时回读 `novel/draft/chapters/**`

### 11.2 回读正文的“精准定位”原则

- 先用检索定位，再打开文件；避免“把整章/整卷塞进上下文”。
- 检索关键词优先用：实体 ID（`char-*`/`loc-*`/`thr-*`）、专名、独特物件名、关键事件标签。

### 11.3 文件更新纪律（防止平行宇宙）

- 任何“权威事实”只写入 `novel/bible/` 与 `novel/continuity/`，正文不承担设定存储职责。
- 新增设定或改设定：必须补一条 `novel/decisions/decision-log.md`（至少写“为何改、影响哪些章节/场景、回修计划”）。
- 写作输出后强制闭环：更新 `novel/summaries/chapters/` + `novel/summaries/state.md` + `novel/continuity/open-threads.md`（参见 4.4）。

### 11.4 反馈循环（让系统越写越稳）

- 每写 1 章：`novel-summarizing` + `novel-thread-tracking`
- 每写 2~3 章或每次大改：`novel-continuity-checking` 出报告并清单化回修
- 每卷结束：生成卷摘要（`novel/summaries/volumes/`），并把“承诺清单”与“回收清单”对账一次

### 11.5 任何不确定都“显式化”

- 不确定的事实一律标注为 TODO，并落到 `novel/continuity/issues.md`，不要在正文里“默认补全”。
- 当用户要求“直接写下去”但缺关键设定时：先提 1~3 个最小澄清问题；若用户拒绝澄清，则给出 1 个默认假设并写入决策记录。

### 11.6 冲突处理优先级（canon 优先）

- 权威优先级：`novel/bible/` > `novel/continuity/` > `novel/summaries/` > `novel/draft/`
- 当正文与权威事实冲突时：不要私自“改设定去迎合正文”；先在 `novel/continuity/issues.md` 记录冲突，并提出 1 个最小改动修复方案（改正文或改设定二选一，给出代价）。

### 11.7 请求分流（路由）规则（总控 Skill 使用）

- 用户要“写/续写/扩写章节” → `novel-chapter-drafting`（必要时先 `novel-scene-planning`）
- 用户要“总结/回顾/梳理目前进度” → `novel-summarizing`（更新 state 与章摘要）
- 用户要“伏笔/线索/回收安排” → `novel-thread-tracking`
- 用户要“查错/核对时间线/设定一致性” → `novel-continuity-checking`
- 用户要“改设定/人物卡/世界观条目” → `novel-bible-managing`（重大改动同步 `novel/decisions/decision-log.md`）
- 用户要“润色/二稿/结构大修” → `novel-editing`（大改后跑 continuity + summaries 闭环）
