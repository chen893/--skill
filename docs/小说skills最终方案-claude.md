# 长篇小说多Skill系统设计 - 最终方案

> 融合Claude方案的精细化管理与GPT方案的流程化协作，构建稳健的长篇小说创作系统。

---

## 版本信息

| 版本 | 日期 | 说明 |
|------|------|------|
| v1.0 | 2025-12-25 | 融合Claude v1.1与GPT方案的最终版本 |

---

## 目录

1. [设计理念](#设计理念)
2. [架构总览](#架构总览)
3. [Skill体系设计](#skill体系设计)
4. [数据管理架构](#数据管理架构)
5. [上下文管理策略](#上下文管理策略)
6. [工作流设计](#工作流设计)
7. [类型适配配置](#类型适配配置)
8. [评估体系](#评估体系)
9. [实施指南](#实施指南)

---

## 设计理念

### 融合原则

本方案融合两个前序方案的优势，规避其关键劣势：

| 融合来源 | 采纳内容 | 规避问题 |
|---------|---------|---------|
| **Claude方案** | 8核心Skill设计、类型参数配置、评估体系、上下文预算 | 增加总控Skill解决协调问题 |
| **GPT方案** | 总控机制、实用模板、系统协议、决策记录、DoD | 合并Skill减少碎片化 |

### 核心设计决策

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              五大设计决策                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  1. 总控优先        2. 双格式存储        3. 类型驱动                         │
│  ─────────────      ─────────────        ─────────────                       │
│  显式路由Skill      JSON(程序) +         genre_config                        │
│  协调所有Skill      Markdown(人读)       预设适配各类型                      │
│                                                                             │
│  4. 闭环验证        5. 决策可追溯                                            │
│  ─────────────      ─────────────                                            │
│  DoD + 评估体系     重大改动必记录                                           │
│  保证每步完成       影响范围可追溯                                           │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 架构总览

### Skill架构图

```
                              ┌─────────────────────────────────────┐
                              │       novel-orchestrating           │
                              │     （总控：路由、协调、状态）         │
                              └──────────────┬──────────────────────┘
                                             │
          ┌──────────────────┬───────────────┼───────────────┬──────────────────┐
          │                  │               │               │                  │
          ▼                  ▼               ▼               ▼                  ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐ │
│  worldbuilding  │ │   characters    │ │ plot-outlining  │ │ scene-planning  │ │
│  （世界观构建）   │ │  （角色管理）    │ │  （剧情规划）    │ │  （场景设计）    │ │
└────────┬────────┘ └────────┬────────┘ └────────┬────────┘ └────────┬────────┘ │
         │                   │                   │                   │          │
         └───────────────────┴─────────┬─────────┴───────────────────┘          │
                                       │                                        │
                            ┌──────────┴──────────┐                             │
                            │    prose-crafting   │                             │
                            │    （正文写作）       │                             │
                            └──────────┬──────────┘                             │
                                       │                                        │
                     ┌─────────────────┼─────────────────┐                      │
                     │                 │                 │                      │
                     ▼                 ▼                 ▼                      │
          ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
          │   summarizing   │ │continuity-check-│ │   reviewing     │
          │  （摘要生成）     │ │ing（一致性追踪） │ │  （稿件审阅）    │
          └─────────────────┘ └─────────────────┘ └─────────────────┘

                                       │
                     ┌─────────────────┴─────────────────┐
                     │          数据层 (Data Layer)       │
                     │   JSON(结构化) + Markdown(可读)    │
                     └───────────────────────────────────┘
```

### Skill数量控制

| 层级 | Skill | 数量 | 说明 |
|------|-------|------|------|
| 总控层 | novel-orchestrating | 1 | 路由、协调、状态管理 |
| 设定层 | worldbuilding, characters | 2 | 世界观与角色分离 |
| 规划层 | plot-outlining, scene-planning | 2 | 大纲与场景分离 |
| 写作层 | prose-crafting | 1 | 核心写作Skill |
| 验证层 | summarizing, continuity-checking, reviewing | 3 | 摘要、一致性、审阅 |
| **合计** | | **9** | 比Claude方案+1总控，比GPT方案-6 |

---

## Skill体系设计

### 1. novel-orchestrating（总控）

> **来源**：GPT方案，解决Claude方案缺少路由的问题

```yaml
---
name: novel-orchestrating
description: |
  协调长篇小说项目的全流程：路由用户请求到正确Skill、控制上下文读取范围、
  维护进度状态、提供阶段建议。
  触发词：项目、进度、状态、接下来、下一步、开始、继续、计划。
  当用户不确定该做什么、需要项目总览、或进行跨Skill操作时使用。
---
```

**核心职责**：

```
✅ 负责：                          ❌ 不负责：
├── 请求路由（分发到正确Skill）      ├── 具体创作工作
├── 上下文控制（决定读什么文件）     ├── 内容生成
├── 进度管理（追踪当前阶段）         ├── 质量判断
├── 状态查询（汇总项目信息）         └── 一致性检查
├── 阶段建议（推荐下一步）
└── 闭环验证（确认DoD完成）
```

**路由规则**（系统协议）：

| 用户请求关键词 | 路由目标 |
|--------------|---------|
| 写/续写/扩写/正文/对话/描写 | → prose-crafting |
| 设定/世界观/地理/历史/势力 | → worldbuilding |
| 角色/人物/人设/关系 | → characters |
| 大纲/结构/剧情/主线/支线 | → plot-outlining |
| 场景卡/场景设计/分镜/这一章怎么写 | → scene-planning |
| 总结/摘要/回顾/state/搜索前文 | → summarizing |
| 伏笔/线索/一致性/矛盾/时间线 | → continuity-checking |
| 审阅/润色/优化/逻辑问题/节奏 | → reviewing |

---

### 2. worldbuilding（世界观构建）

> **来源**：Claude方案，保持独立

```yaml
---
name: worldbuilding
description: |
  构建和管理小说世界观设定，包括地理、历史、社会结构、力量体系、规则系统。
  触发词：世界观、设定、地理、历史、修炼体系、魔法系统、势力、宗门、规则。
  在创建新世界、扩展设定或查询已有设定时使用。
---
```

**职责边界**：

```
✅ 负责：                          ❌ 不负责：
├── 创建世界设定                    ├── 角色背景（→ characters）
├── 扩展已有设定                    ├── 设定使用一致性（→ continuity-checking）
├── 记录设定到数据文件              └── 写作中的设定引用（→ prose-crafting）
├── 查询设定内容
└── 设定创建时的自洽验证
```

---

### 3. characters（角色管理）

> **来源**：Claude方案character-managing，简化命名

```yaml
---
name: characters
description: |
  管理小说角色档案、追踪关系网络、设计成长弧线、定义语言风格。
  触发词：角色、人物、主角、配角、反派、关系、人设、性格、背景、弧线。
  在创建角色、查询角色信息、分析角色关系或设计角色发展时使用。
---
```

**职责边界**：

```
✅ 负责：                          ❌ 不负责：
├── 创建角色档案                    ├── 角色在章节中的具体表现（→ prose-crafting）
├── 管理角色关系网络                ├── 角色出场的一致性检查（→ continuity-checking）
├── 设计角色弧线                    ├── 角色相关的剧情线（→ plot-outlining）
├── 定义角色语言风格                └── 角色状态快照维护（→ continuity-checking）
├── 更新角色权威档案(bible/)
└── 查询角色信息

**数据更新边界**：
- characters更新：`bible/characters/char-*.json`（权威档案）
- continuity-checking更新：`continuity/character-states.json`（状态快照）
```

---

### 4. plot-outlining（剧情规划）

> **来源**：合并Claude方案plot-architecting与GPT方案novel-outlining

```yaml
---
name: plot-outlining
description: |
  设计故事结构、规划剧情线、创建章节大纲、管理主线/支线。
  触发词：剧情、大纲、结构、章节规划、主线、支线、冲突、高潮、转折。
  在构思故事框架、设计冲突、规划章节或调整剧情走向时使用。
---
```

**大纲层级**：

```
故事结构 (master-outline)
└── 卷大纲 (volume-outline)
    └── 弧大纲 (arc-outline)
        └── 章节大纲 (chapter-outline)
            └── → 交给scene-planning细化为场景卡
```

---

### 5. scene-planning（场景设计）

> **来源**：GPT方案novel-scene-planning，Claude方案缺失

```yaml
---
name: scene-planning
description: |
  将章节大纲拆解为可执行的场景卡，明确每个场景的目标-冲突-结果。
  触发词：场景、分镜、场景卡、这一章怎么写、冲突设计、节奏。
  在拿到章节大纲后、开始写作前使用。
---
```

**场景卡模板**（来自GPT方案）：

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

# 场景卡：[一句话概述]

## 目标（Goal）
[POV角色在本场景想要达成什么]

## 冲突（Conflict）
[阻碍目标达成的障碍是什么]

## 结果（Outcome）
[场景结束时的状态变化]

## 关键节拍（Beats）
1. [节拍1]
2. [节拍2]
3. [节拍3]

## 信息揭示 / 伏笔
- 埋设：[如有]
- 回收：[如有]

## 连续性约束
- [必须满足的约束条件]
```

---

### 6. prose-crafting（正文写作）

> **来源**：Claude方案，核心写作Skill

```yaml
---
name: prose-crafting
description: |
  控制写作风格，撰写章节正文，处理对话和描写，营造场景氛围。
  触发词：写、撰写、正文、文风、风格、对话、描写、视角。
  在撰写章节正文、调整文风或创作具体内容时使用。
  注意：场景规划请使用scene-planning，本Skill负责场景的具体写作。
---
```

**风格参数**（来自Claude方案）：

```json
{
  "style_parameters": {
    "tone": ["轻松", "沉稳", "热血", "压抑", "诙谐", "冷峻"],
    "vocabulary": ["口语化", "书面化", "古风", "现代", "混合"],
    "sentence_length": ["短句为主", "长句为主", "混合", "节奏变化"],
    "description_density": "[0.2-0.8]",
    "dialogue_ratio": "[0.2-0.7]",
    "pacing": ["快节奏", "慢节奏", "张弛有度"]
  }
}
```

---

### 7. summarizing（摘要生成）

> **来源**：合并Claude方案content-indexing与GPT方案novel-summarizing

```yaml
---
name: summarizing
description: |
  生成并维护分层摘要（章/卷/state）、检索已写内容、查找特定信息。
  触发词：总结、摘要、搜索、查找、之前写过、回顾、state、前文。
  在完成章节后生成摘要、需要查找前文内容、或加载写作上下文时使用。
---
```

**核心功能**：

1. **摘要生成**：章节摘要 → 卷摘要 → state.md
2. **内容检索**：关键词搜索、角色出场检索、情节检索
3. **上下文加载**：为prose-crafting准备写作所需的上下文包

---

### 8. continuity-checking（一致性追踪）

> **来源**：合并Claude方案continuity-tracking与GPT方案novel-thread-tracking + novel-continuity-checking

```yaml
---
name: continuity-checking
description: |
  追踪故事时间线、检查事实一致性、管理伏笔/线索的埋设与回收。
  触发词：时间线、一致性、矛盾、伏笔、线索、回收、连续性、事实核查。
  在检查内容一致性、管理伏笔、验证时间线或发现冲突时使用。
---
```

**职责范围**：

```
✅ 负责：                          ❌ 不负责：
├── 时间线管理                      ├── 叙事合理性（→ reviewing）
├── 事实一致性检查                  ├── 文字质量（→ reviewing）
├── 伏笔/线索追踪（open-threads）    └── 剧情逻辑（→ plot-outlining）
├── 角色状态追踪
├── 设定使用一致性
└── 生成连续性报告
```

**线索清单模板**（来自GPT方案）：

```markdown
# 未收束线索清单（open-threads）

| thread_id | 标题 | 类型 | 首次出现 | 当前状态 | 预计回收窗口 | 回收章节 |
|-----------|------|------|---------|---------|-------------|---------|
| thr-0007 | 神秘玉佩 | 伏笔 | ch-003 | open | ch-040~ch-060 | |

## 维护规则
- 新线索：写入表格 + 章节摘要threads_open
- 回收线索：填写回收章节 + 章节摘要threads_close + 状态改为closed
```

---

### 9. reviewing（稿件审阅）

> **来源**：合并Claude方案manuscript-reviewing与GPT方案novel-editing

```yaml
---
name: reviewing
description: |
  审阅稿件质量，检查逻辑漏洞，分析节奏曲线，提供润色和修订建议。
  触发词：审阅、检查、修改、润色、问题、逻辑、节奏、优化、二稿。
  在完成章节后进行质量检查、需要修订建议或润色时使用。
---
```

**审阅维度**：

| 维度 | 检查内容 |
|------|---------|
| 逻辑审阅 | 角色行为动机、事件因果、冲突解决 |
| 节奏审阅 | 场景长度、张力曲线、拖沓/仓促 |
| 文字审阅 | 重复用词、句式单调、描写恰当性 |
| 角色审阅 | 对话符合人设、情感变化铺垫、弧线推进 |

---

## 数据管理架构

### 双格式存储策略

| 数据类型 | 格式 | 理由 |
|---------|------|------|
| 核心配置（project.json） | JSON | 程序化读取、类型参数配置 |
| 角色档案 | JSON + Markdown | JSON存结构化数据，Markdown存描述性内容 |
| 世界设定 | JSON + Markdown | 同上 |
| 章节正文 | Markdown | 人工可读写 |
| 章节摘要 | Markdown | 人工可快速浏览 |
| 场景卡 | Markdown（带Frontmatter） | 人工可编辑，Frontmatter提供结构 |
| 线索清单 | Markdown（表格） | 人工可快速查看 |
| 时间线 | Markdown（表格） | 人工可快速查看 |
| 决策记录 | Markdown（表格） | 人工可追溯 |
| 元数据索引 | JSON | 程序化索引 |

### 目录结构

```
novel-project/
│
├── config/                           # 配置层
│   ├── project.json                  # 项目元配置
│   ├── genre-config.json             # 类型参数配置
│   └── style-guide.md                # 风格指南（人工可读）
│
├── bible/                            # 小说圣经（权威设定）
│   ├── world/
│   │   ├── world-bible.json          # 世界设定索引
│   │   ├── geography/
│   │   │   └── loc-*.md              # 地点设定（Markdown）
│   │   ├── history/
│   │   │   └── history-timeline.md   # 历史时间线（世界背景设定）
│   │   ├── factions/
│   │   │   └── fac-*.md              # 势力设定
│   │   └── systems/
│   │       └── sys-*.md              # 规则系统（力量体系等）
│   │
│   ├── characters/
│   │   ├── index.json                # 角色索引
│   │   ├── char-*.json               # 角色结构化数据
│   │   └── char-*.md                 # 角色描述性内容
│   │
│   └── glossary.md                   # 专有名词表
│
├── outline/                          # 大纲层
│   ├── master-outline.md             # 总大纲
│   ├── arcs/
│   │   └── arc-*.md                  # 故事弧大纲
│   ├── volumes/
│   │   └── vol-*-outline.md          # 卷大纲
│   └── scenes/
│       └── scn-*.md                  # 场景卡
│
├── draft/                            # 草稿层
│   ├── chapters/
│   │   ├── ch-001.md                 # 章节正文
│   │   ├── ch-002.md
│   │   └── ...
│   └── wip/                          # 进行中的草稿
│       └── ch-xxx-draft.md
│
├── summaries/                        # 摘要层
│   ├── state.md                      # 当前故事状态（核心！）
│   ├── chapters/
│   │   └── ch-*-summary.md           # 章节摘要
│   └── volumes/
│       └── vol-*-summary.md          # 卷摘要
│
├── continuity/                       # 连续性追踪
│   ├── story-timeline.md             # 故事时间线（情节事件追踪）
│   ├── open-threads.md               # 未收束线索
│   ├── character-states.json         # 角色状态快照
│   └── issues.md                     # 已知连续性问题
│
├── decisions/                        # 决策记录
│   └── decision-log.md               # 重大改动记录
│
├── reports/                          # 报告
│   ├── continuity/
│   │   └── report-*.md               # 连续性检查报告
│   └── review/
│       └── review-*.md               # 审阅报告
│
└── progress/                         # 进度追踪
    ├── status.json                   # 项目状态（程序读取：完成章节数、字数、阶段）
    └── milestones.json               # 里程碑

**状态文件职责区分**：
- `summaries/state.md`：**故事状态**（情节进展、角色现状、约束条件）- 人工可读
- `progress/status.json`：**项目状态**（元数据统计、完成进度）- 程序读取
```

### 核心数据文件规格

#### 1. 项目配置 (config/project.json)

```json
{
  "project_id": "novel-001",
  "title": "小说名称",
  "genre": "玄幻",
  "target_words": 500000,
  "chapter_avg_words": 3000,
  "created_at": "2025-01-01T00:00:00Z",
  "updated_at": "2025-12-25T00:00:00Z",
  "current_phase": "writing",
  "current_chapter": "ch-025",
  "skills_enabled": ["all"],
  "genre_config_ref": "genre-config.json"
}
```

#### 2. 角色档案 (bible/characters/char-*.json)

```json
{
  "id": "char-001",
  "name": "林雨",
  "aliases": ["小雨", "雨少"],
  "role": "protagonist",
  "pov": true,
  "first_appearance": "ch-001",
  "tags": ["学生", "天才"],
  "basic": {
    "age_at_start": 16,
    "gender": "male",
    "appearance": {
      "height": "175cm",
      "features": ["黑发", "剑眉"]
    }
  },
  "personality": {
    "traits": ["坚韧", "沉默寡言"],
    "flaws": ["过于执着"],
    "mbti": "INTJ"
  },
  "arc": {
    "type": "positive",
    "start_state": "弱小少年",
    "end_state": "担当强者",
    "key_turning_points": ["ch-015", "ch-050", "ch-100"]
  },
  "voice": {
    "speech_pattern": "简洁直接",
    "catchphrases": [],
    "vocabulary_level": "中等"
  },
  "relationships": {
    "char-002": {"type": "mentor", "status": "active"}
  },
  "detail_file": "char-001.md"
}
```

#### 3. 当前状态 (summaries/state.md)

> 来自GPT方案，最重要的上下文入口

```markdown
# 当前故事状态（state）

> 最后更新：2025-12-25（ch-025完成后）

## 故事进度
- 已完成：ch-001 ~ ch-025
- 当前时间线：D+45
- 当前地点：loc-imperial-city
- 当前POV：char-001（林雨）

## 主线现状
林雨已进入帝都，正在参加宗门大比选拔。上一章他通过了第一轮考核，
但暴露了特殊体质，引起了神秘势力的注意。

## 关键人物现状
- char-001（林雨）：筑基期三层，情绪紧张，目标通过选拔
- char-002（师父）：不在场，上一次出现ch-020
- char-003（女主）：同在选拔现场，尚未与主角正式相遇

## 关键约束（不可违反）
- 林雨不知道自己的身世秘密
- 玉佩的秘密尚未揭示（thr-0007待回收）
- 帝都距离边陲小镇需要1个月路程

## 近期写作目标（接下来3章）
- ch-026：第二轮考核，与女主初次交锋
- ch-027：考核意外，神秘势力介入
- ch-028：危机中突破，通过选拔
```

#### 4. 决策记录 (decisions/decision-log.md)

> 来自GPT方案，解决Claude方案缺失的问题

```markdown
# 决策记录（Decision Log）

> 目标：把重大设定/剧情改动的"原因与代价"记录清楚，避免蝴蝶效应。

| ID | 日期 | 决策 | 原因 | 影响范围 | 回修清单 | 状态 |
|----|------|------|------|---------|---------|------|
| dec-001 | 2025-12-20 | 将主角初始年龄从18改为16 | 更符合成长型人设 | ch-001~ch-010 | [x]ch-001 [x]ch-005 | done |
| dec-002 | 2025-12-25 | 增加玉佩发光的次数限制（每月一次） | 避免过于万能 | ch-003, ch-020, 后续 | [ ]ch-020 | in-progress |

## 规则
- 任何"会影响既有章节或设定一致性"的改动都必须登记
- 影响范围必须可定位：章节范围 + 实体ID
- 回修清单完成后状态改为done
```

---

## 上下文管理策略

### 阅读优先级协议

> 融合Claude方案的预算分配与GPT方案的优先级原则

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           上下文阅读协议                                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  优先级1（必读）：                                                           │
│  ├── summaries/state.md              ～500 tokens                          │
│  └── 本章场景卡 scn-*.md             ～300 tokens                          │
│                                                                             │
│  优先级2（按需读）：                                                         │
│  ├── 涉及角色档案 char-*.json        ～500 tokens                          │
│  ├── 上一章摘要 ch-*-summary.md      ～300 tokens                          │
│  └── 相关设定摘要                    ～300 tokens                          │
│                                                                             │
│  优先级3（检索后读）：                                                       │
│  ├── 正文片段（仅在发现冲突时）                                              │
│  ├── 详细设定（仅首次涉及时）                                                │
│  └── 历史章节摘要                                                           │
│                                                                             │
│  禁止：直接读取全部正文                                                      │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 上下文预算分配

#### 标准写作会话（8K tokens可用）

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  Token预算分配                                                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  [Skill指令]               1000 tokens  █████                              │
│  [state.md]                 500 tokens  ███                                │
│  [场景卡]                   300 tokens  ██                                 │
│  [角色档案]                 500 tokens  ███                                │
│  [上一章摘要]               300 tokens  ██                                 │
│  [相关设定]                 300 tokens  ██                                 │
│  [对话缓冲]                 600 tokens  ███                                │
│  ──────────────────────────────────                                        │
│  [生成预留]                4500 tokens  ██████████████████████             │
│                                                                             │
│  总计：8000 tokens                                                          │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 分层摘要体系

```
全书摘要 (1000字) ─ 可选，完结后生成
└── 卷摘要 (每卷500字) ─ 每卷结束时生成
    └── 章节摘要 (每章100-200字) ─ 每章完成后必须生成
        └── 章节正文 (每章3000字)

当前状态 state.md (500字) ─ 每章完成后必须更新
```

**卷摘要使用时机**：
- 跨卷写作时（如开始新卷第一章），加载上一卷摘要作为背景
- 大修工作流中，需要回顾整卷情节时加载
- 人工审阅整体结构时参考
- 日常章节写作**不自动加载**卷摘要，以节省上下文

---

## 工作流设计

### Definition of Done（DoD）

> 来自GPT方案，解决Claude方案缺失的问题

**每完成一章，必须更新**：

| 必更新文件 | 负责Skill | 说明 |
|-----------|----------|------|
| draft/chapters/ch-xxx.md | prose-crafting | 章节正文 |
| summaries/chapters/ch-xxx-summary.md | summarizing | 章节摘要 |
| summaries/state.md | summarizing | 当前状态 |
| continuity/open-threads.md | continuity-checking | 线索更新 |

**可选更新**（如有变化）：

- continuity/story-timeline.md（时间线推进）
- continuity/character-states.json（角色状态快照）
- bible/characters/char-*.json（角色权威档案变更）

### 工作流总览

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                             四大工作流                                        │
└─────────────────────────────────────────────────────────────────────────────┘

1. 开坑工作流（从0到1）
   novel-orchestrating → worldbuilding → characters → plot-outlining → scene-planning

2. 写章工作流（日常循环）
   summarizing(加载上下文) → prose-crafting(写正文) → summarizing(生成摘要)
   → continuity-checking(检查一致性) → reviewing(质量审阅) → DoD闭环

3. 大修工作流（结构性修订）
   reviewing(审阅) → plot-outlining(调整结构) → prose-crafting(修改)
   → continuity-checking(验证) → summarizing(更新摘要)

4. 设定变更工作流（Retcon）
   decisions/decision-log.md(登记) → worldbuilding/characters(修改设定)
   → continuity-checking(影响评估) → prose-crafting(回修正文) → summarizing(更新摘要)
```

### 写章工作流详解

```markdown
## 单章写作流程

### 准备阶段（novel-orchestrating协调）
- [ ] 1. 确认章节号和场景卡已准备
- [ ] 2. 调用summarizing加载上下文包：
      - state.md
      - 场景卡 scn-*.md
      - 涉及角色档案
      - 上一章摘要
      - 待处理伏笔列表

### 写作阶段（prose-crafting执行）
- [ ] 3. 按场景卡分段撰写
- [ ] 4. 遵循style-guide.md风格参数
- [ ] 5. 注意角色语言风格一致
- [ ] 6. 设置章末钩子

### 验证阶段（多Skill协作）
- [ ] 7. continuity-checking：一致性检查
      - 事实一致性
      - 时间线一致性
      - 角色状态一致性
- [ ] 8. reviewing：质量审阅
      - 逻辑合理性
      - 节奏分析
      - 文字质量

### 修订阶段（如需）
- [ ] 9. 根据审阅意见修订
- [ ] 10. 重新验证（返回步骤7）
- [ ] 最多3轮迭代

### 闭环阶段（DoD）
- [ ] 11. summarizing生成章节摘要
- [ ] 12. summarizing更新state.md
- [ ] 13. continuity-checking更新open-threads.md
- [ ] 14. 更新progress/status.json

✅ 章节完成
```

### 设定变更工作流详解

> 来自GPT方案，防止"改一处崩全书"

```markdown
## 设定变更安全流程

### 登记阶段
1. 在decisions/decision-log.md登记：
   - 决策内容
   - 变更原因
   - 替代方案（考虑过但放弃的）
   - 影响范围（章节 + 实体ID）
   - 回修清单

### 修改阶段
2. worldbuilding/characters更新权威设定（bible/）
3. continuity-checking评估影响范围
4. 生成详细的回修清单

### 回修阶段
5. prose-crafting按回修清单逐章修正
6. continuity-checking验证每章修正
7. 标记回修清单完成项

### 同步阶段
8. summarizing更新受影响章节摘要
9. summarizing更新state.md
10. continuity-checking检查open-threads是否需要调整回收窗口
11. 将decision状态改为done
```

---

## 类型适配配置

> 来自Claude方案，GPT方案缺失

### genre-config.json

```json
{
  "genre_configs": {
    "玄幻": {
      "worldbuilding": {
        "power_system": {
          "type": "cultivation",
          "levels": ["练气", "筑基", "金丹", "元婴", "化神"],
          "resources": ["灵石", "丹药", "法宝"]
        },
        "world_scale": "multiverse",
        "factions": true
      },
      "characters": {
        "power_tracking": true,
        "relationship_complexity": "medium"
      },
      "plot-outlining": {
        "structure": "升级流",
        "conflict_types": ["实力压制", "资源争夺", "势力对抗"],
        "pacing": "爽点驱动"
      },
      "prose-crafting": {
        "style_preset": "wuxia",
        "action_scenes": {"frequency": "high", "detail_level": "medium"},
        "vocabulary": "古风混合"
      },
      "continuity-checking": {
        "power_level_strict": true,
        "artifact_tracking": true
      }
    },

    "言情": {
      "worldbuilding": {
        "power_system": null,
        "world_scale": "realistic",
        "social_detail": "high"
      },
      "characters": {
        "emotion_tracking": true,
        "relationship_complexity": "high",
        "inner_monologue": true
      },
      "plot-outlining": {
        "structure": "情感线驱动",
        "conflict_types": ["误会", "身份障碍", "情敌", "家庭反对"],
        "pacing": "情感节奏"
      },
      "prose-crafting": {
        "style_preset": "romance",
        "dialogue_heavy": true,
        "emotion_description": "detailed"
      },
      "continuity-checking": {
        "relationship_state_strict": true,
        "emotion_continuity": true
      }
    },

    "悬疑": {
      "worldbuilding": {
        "power_system": null,
        "world_scale": "realistic",
        "detail_accuracy": "critical"
      },
      "characters": {
        "secret_tracking": true,
        "alibi_management": true,
        "motive_tracking": true
      },
      "plot-outlining": {
        "structure": "多线交织",
        "information_control": true,
        "twist_planning": true,
        "fair_play": true
      },
      "prose-crafting": {
        "style_preset": "suspense",
        "red_herrings": true,
        "tension_building": true
      },
      "continuity-checking": {
        "clue_tracking": true,
        "timeline_strict": true,
        "logic_verification": "critical"
      },
      "reviewing": {
        "logic_check_level": "exhaustive",
        "reader_deduction_check": true
      }
    }
  }
}
```

---

## 评估体系

> 来自Claude方案，GPT方案缺失

### 评估场景定义

```json
{
  "evaluations": [
    {
      "id": "eval-001",
      "name": "单章写作",
      "description": "从场景卡撰写完整章节",
      "skills_tested": ["prose-crafting", "characters", "summarizing"],
      "input": "按照场景卡撰写一个约3000字的章节",
      "success_criteria": {
        "word_count": {"min": 2700, "max": 3300},
        "scene_coverage": "all_beats_covered",
        "character_voice": "consistent_with_profile",
        "continuity_errors": 0,
        "dod_completed": true
      }
    },
    {
      "id": "eval-002",
      "name": "一致性检测",
      "description": "发现植入的一致性错误",
      "skills_tested": ["continuity-checking", "summarizing"],
      "setup": "章节包含3个故意植入的错误",
      "success_criteria": {
        "detection_rate": 1.0,
        "false_positives": {"max": 1},
        "fix_suggestions": "actionable"
      }
    },
    {
      "id": "eval-003",
      "name": "伏笔回收",
      "description": "自然回收之前埋设的伏笔",
      "skills_tested": ["prose-crafting", "continuity-checking", "summarizing"],
      "success_criteria": {
        "original_reference": "included",
        "integration": "natural",
        "threads_updated": true
      }
    },
    {
      "id": "eval-004",
      "name": "设定变更",
      "description": "安全执行设定修改并完成回修",
      "skills_tested": ["worldbuilding", "characters", "continuity-checking", "prose-crafting", "summarizing"],
      "success_criteria": {
        "decision_logged": true,
        "impact_assessed": true,
        "chapters_fixed": "all_in_list",
        "no_new_inconsistencies": true
      }
    }
  ]
}
```

### 监控指标

| 指标 | 目标 | 测量方式 |
|------|------|---------|
| Skill路由准确率 | >90% | 用户意图与触发Skill匹配 |
| DoD完成率 | 100% | 每章4个必更新文件都已更新 |
| 一致性错误率 | <5% | continuity-checking报告的问题数 |
| 上下文加载成功率 | >95% | 正确加载所需上下文 |
| 决策记录完整率 | 100% | 重大改动都有decision记录 |

---

## 实施指南

### 第一阶段：基础设施搭建

```bash
# 1. 创建Skill目录结构
mkdir -p novel-skills/{novel-orchestrating,worldbuilding,characters,plot-outlining,scene-planning,prose-crafting,summarizing,continuity-checking,reviewing}/{assets,references}

# 2. 创建数据目录结构
mkdir -p novel-project/{config,bible/{world/{geography,history,factions,systems},characters},outline/{arcs,volumes,scenes},draft/{chapters,wip},summaries/{chapters,volumes},continuity,decisions,reports/{continuity,review},progress}

# 3. 初始化核心文件
touch novel-skills/*/SKILL.md
touch novel-project/config/project.json
touch novel-project/config/genre-config.json
touch novel-project/summaries/state.md
touch novel-project/decisions/decision-log.md
touch novel-project/continuity/open-threads.md
```

### 第二阶段：Skill实现顺序

| 顺序 | Skill | 优先级 | 依赖 |
|------|-------|-------|------|
| 1 | novel-orchestrating | P0 | 无（总控必须先有） |
| 2 | worldbuilding | P0 | 总控 |
| 3 | characters | P0 | 总控 |
| 4 | plot-outlining | P0 | 总控 |
| 5 | scene-planning | P1 | plot-outlining |
| 6 | prose-crafting | P0 | scene-planning |
| 7 | summarizing | P0 | prose-crafting |
| 8 | continuity-checking | P0 | summarizing |
| 9 | reviewing | P1 | continuity-checking |

### 第三阶段：验证清单

- [ ] 总控路由测试：不同请求是否分发到正确Skill
- [ ] DoD闭环测试：写完一章后4个文件是否都更新
- [ ] 上下文加载测试：写作时是否正确加载state+场景卡+角色
- [ ] 一致性检测测试：植入错误能否被发现
- [ ] 设定变更测试：decision-log是否完整记录
- [ ] 评估场景测试：4个评估场景是否通过

### 常见问题处理

| 问题 | 可能原因 | 解决方案 |
|------|---------|---------|
| Skill未触发 | description触发词不足 | 增加触发词覆盖 |
| 错误Skill触发 | 职责边界模糊 | 明确边界，调整description |
| DoD未完成 | 闭环意识不强 | 强制检查DoD清单 |
| 一致性错误 | 数据未及时更新 | 强化更新触发 |
| 上下文不足 | 加载优先级不当 | 严格遵循阅读协议 |

---

## 附录

### A. 与前序方案对比

| 特性 | Claude方案 | GPT方案 | 本方案 |
|------|-----------|--------|-------|
| Skill数量 | 8 | 15+ | **9** |
| 总控机制 | ❌ | ✅ | **✅** |
| 角色独立Skill | ✅ | ❌ | **✅** |
| 场景卡 | ❌ | ✅ | **✅** |
| 决策记录 | ❌ | ✅ | **✅** |
| DoD | ❌ | ✅ | **✅** |
| 类型参数配置 | ✅ | ❌ | **✅** |
| 评估体系 | ✅ | ❌ | **✅** |
| 上下文预算 | ✅ | ❌ | **✅** |
| 双格式存储 | ❌ | ❌ | **✅** |

### B. Skill元数据清单

| Skill | 核心触发词 |
|-------|-----------|
| novel-orchestrating | 项目、进度、状态、接下来、开始、继续 |
| worldbuilding | 世界观、设定、地理、历史、势力、规则、宗门 |
| characters | 角色、人物、人设、关系、弧线、性格 |
| plot-outlining | 剧情、大纲、结构、主线、支线、冲突、转折 |
| scene-planning | 场景卡、场景设计、分镜、这一章怎么写 |
| prose-crafting | 写、撰写、正文、文风、对话、描写、视角 |
| summarizing | 总结、摘要、搜索前文、state、回顾 |
| continuity-checking | 时间线、一致性、伏笔、线索、矛盾、事实核查 |
| reviewing | 审阅、润色、优化、逻辑问题、节奏、二稿 |

### C. 文件行数限制

| 文件类型 | 行数限制 |
|---------|---------|
| SKILL.md | <300行 |
| 详细指南 *.md | <500行 |
| 场景卡 scn-*.md | <100行 |
| 章节摘要 | <50行 |
| state.md | <100行 |

### D. 文件命名约定

| 文件类型 | 命名规则 | 示例 |
|---------|---------|------|
| 角色档案 | char-[id].json/md | char-001.json, char-lin-yu.md |
| 地点设定 | loc-[name].md | loc-imperial-city.md |
| 势力设定 | fac-[name].md | fac-sword-sect.md |
| 规则系统 | sys-[name].md | sys-cultivation.md |
| 故事弧 | arc-[name].md | arc-revenge.md |
| 场景卡 | scn-[chapter]-[seq].md | scn-001-01.md |
| 章节 | ch-[number].md | ch-001.md |
| 线索 | thr-[number] | thr-0007 |

---

*文档版本：1.0.1*
*创建日期：2025-12-25*
*最后更新：2025-12-25（修复冲突审查发现的7个问题）*
*设计依据：融合Claude方案v1.1与GPT方案*
