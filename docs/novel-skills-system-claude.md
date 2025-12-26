# 长篇小说多Skill系统设计规格 v1.1

> 一个模块化的Agent Skills系统，用于支撑数十万字长篇小说的创作与管理。

---

## 版本历史

| 版本 | 日期 | 变更说明 |
|------|------|----------|
| v1.1 | 2025-12 | 增加数据管理架构、上下文策略、细化模板、修复格式问题 |
| v1.0 | 2025-12 | 初始版本 |

---

## 目录

1. [系统概述](#系统概述)
2. [数据管理架构](#数据管理架构) *(v1.1新增)*
3. [上下文管理策略](#上下文管理策略) *(v1.1新增)*
4. [架构设计](#架构设计)
5. [核心Skill规格](#核心skill规格)
6. [Skill协作工作流](#skill协作工作流)
7. [通用适配机制](#通用适配机制)
8. [完整SKILL.md示例](#完整skillmd示例)
9. [评估体系](#评估体系) *(v1.1新增)*
10. [实施指南](#实施指南)

---

## 系统概述

### 设计目标

长篇小说创作是一项复杂的系统工程，涉及世界观构建、人物塑造、剧情编排、文字创作等多个维度。本系统通过**8个专业化的Agent Skill模块**，为Claude提供：

1. **领域专业知识**：小说创作的方法论、工作流和最佳实践
2. **结构化管理能力**：数十万字内容的一致性追踪与版本管理
3. **协作工作流**：从构思到成稿的全流程支撑
4. **数据持久化**：跨会话的状态管理与内容检索 *(v1.1)*

### 核心挑战与解决方案

| 挑战 | 解决方案 |
|------|----------|
| 数十万字超出上下文窗口 | 分层摘要 + 按需检索机制 |
| 跨会话状态丢失 | 结构化数据文件 + 状态快照 |
| 设定/角色一致性 | 中央数据仓库 + 实时校验 |
| Skill间数据孤岛 | 统一数据层 + 标准接口 |

### 设计原则

```
┌──────────────────────────────────────────────────────────────────────────┐
│                            设计四原则                                     │
├──────────────────────────────────────────────────────────────────────────┤
│  渐进式披露     │  模块化设计     │  简洁优先      │  数据驱动         │
│  ─────────────  │  ─────────────  │  ─────────────  │  ─────────────   │
│  SKILL.md<500行 │  Skill间低耦合  │  只补充Claude   │  所有状态持久化  │
│  按需加载详情   │  支持灵活组合   │  不具备的知识   │  支持跨会话延续  │
└──────────────────────────────────────────────────────────────────────────┘
```

### 适用场景

- 玄幻/仙侠小说（复杂修炼体系、庞大世界观）
- 言情/都市小说（人物关系网络、情感线管理）
- 历史/架空小说（历史事件时间线、文化背景）
- 悬疑/推理小说（伏笔管理、逻辑一致性）
- 科幻小说（科技设定、世界规则）

---

## 数据管理架构

> **v1.1新增**：解决跨会话状态持久化和数据一致性问题

### 数据层概览

```
novel-project-data/                    # 项目数据根目录
│
├── config/                            # 配置层
│   ├── project.json                   # 项目元配置
│   └── genre-settings.json            # 类型参数配置
│
├── world/                             # 世界观数据
│   ├── world-bible.json               # 世界圣经主文件
│   ├── geography/                     # 地理设定
│   │   └── [region-name].json
│   ├── history/                       # 历史事件
│   │   └── timeline.json
│   ├── factions/                      # 势力组织
│   │   └── [faction-name].json
│   └── power-system.json              # 力量体系
│
├── characters/                        # 角色数据
│   ├── index.json                     # 角色索引
│   ├── main/                          # 主要角色
│   │   └── [character-id].json
│   ├── supporting/                    # 配角
│   │   └── [character-id].json
│   └── relationships.json             # 关系网络
│
├── plot/                              # 剧情数据
│   ├── structure.json                 # 故事结构
│   ├── outline/                       # 大纲
│   │   ├── master-outline.json        # 总大纲
│   │   └── volume-[n]/                # 分卷大纲
│   │       └── chapters.json
│   └── plotlines.json                 # 剧情线追踪
│
├── chapters/                          # 章节内容
│   ├── index.json                     # 章节索引
│   ├── volume-1/
│   │   ├── ch001.md                   # 章节正文
│   │   ├── ch001-meta.json            # 章节元数据
│   │   └── ch001-summary.md           # 章节摘要
│   └── volume-2/
│       └── ...
│
├── continuity/                        # 连续性数据
│   ├── timeline.json                  # 故事时间线
│   ├── foreshadowing.json             # 伏笔追踪
│   ├── character-states.json          # 角色状态快照
│   └── fact-registry.json             # 事实注册表
│
├── glossary/                          # 术语表
│   ├── names.json                     # 人名地名
│   ├── terms.json                     # 专有术语
│   └── aliases.json                   # 别名映射
│
└── progress/                          # 进度数据
    ├── status.json                    # 当前状态
    ├── milestones.json                # 里程碑
    └── versions/                      # 版本快照
        └── [timestamp].json
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
  "skills_enabled": [
    "worldbuilding",
    "character-managing",
    "plot-architecting",
    "prose-crafting",
    "continuity-tracking",
    "content-indexing",
    "manuscript-reviewing",
    "novel-project"
  ],
  "genre_config": {
    "worldbuilding": {
      "power_system_type": "cultivation",
      "world_scale": "multiverse"
    },
    "prose-crafting": {
      "style_preset": "wuxia-style",
      "action_weight": 0.4
    }
  }
}
```

#### 2. 角色档案 (characters/main/[id].json)

```json
{
  "id": "char-001",
  "name": "主角名",
  "aliases": ["别名1", "外号"],
  "role": "protagonist",
  "first_appearance": {
    "chapter": 1,
    "context": "开篇场景"
  },
  "basic": {
    "age": 18,
    "age_at_start": 16,
    "gender": "male",
    "appearance": {
      "height": "175cm",
      "build": "清瘦",
      "features": ["黑发", "剑眉"],
      "distinctive_marks": ["左臂疤痕"]
    },
    "personality": {
      "traits": ["坚韧", "沉默寡言", "重情义"],
      "flaws": ["过于执着", "不善表达"],
      "mbti": "INTJ"
    }
  },
  "background": {
    "origin": "边陲小镇",
    "family": {
      "father": {"name": "XXX", "status": "deceased"},
      "mother": {"name": "XXX", "status": "missing"}
    },
    "history": "十岁丧父，母亲失踪...",
    "motivation": {
      "primary": "寻找母亲",
      "secondary": ["变强自保", "为父报仇"]
    },
    "secrets": ["身世之谜"]
  },
  "arc": {
    "type": "positive",
    "start_state": "弱小无助的少年",
    "end_state": "担当大任的强者",
    "key_turning_points": [
      {"chapter": 15, "event": "获得传承"},
      {"chapter": 50, "event": "首次失败"},
      {"chapter": 100, "event": "蜕变成长"}
    ]
  },
  "voice": {
    "speech_pattern": "简洁直接",
    "catchphrases": ["..."],
    "vocabulary_level": "中等偏下（前期）→ 文雅（后期）",
    "dialect": null
  },
  "power": {
    "current_level": "筑基期",
    "abilities": ["剑术", "某功法"],
    "artifacts": ["某剑"],
    "power_history": [
      {"chapter": 1, "level": "凡人"},
      {"chapter": 10, "level": "练气期"},
      {"chapter": 30, "level": "筑基期"}
    ]
  },
  "relationships": {
    "char-002": {
      "type": "mentor",
      "status": "active",
      "history": [
        {"chapter": 5, "relation": "陌生人"},
        {"chapter": 8, "relation": "师徒"}
      ]
    }
  },
  "state_snapshots": {
    "ch050": {
      "location": "某城",
      "emotional_state": "迷茫",
      "goals": ["突破境界"],
      "injuries": null
    }
  }
}
```

#### 3. 章节元数据 (chapters/volume-1/ch001-meta.json)

```json
{
  "chapter_id": "v1-ch001",
  "volume": 1,
  "chapter_number": 1,
  "title": "章节标题",
  "status": "published",
  "word_count": 3150,
  "story_time": {
    "start": "Year1-Month3-Day15-Morning",
    "end": "Year1-Month3-Day15-Noon"
  },
  "pov_character": "char-001",
  "location": ["边陲小镇", "主角家中"],
  "characters_present": ["char-001", "char-002"],
  "events": [
    {"type": "plot", "description": "主角遭遇危机"},
    {"type": "character", "description": "师父出场"}
  ],
  "foreshadowing": {
    "planted": [
      {"id": "fsh-001", "hint": "神秘玉佩发光", "target_chapter": 50}
    ],
    "resolved": []
  },
  "continuity_notes": [
    "主角此时不会游泳",
    "师父尚未透露身份"
  ],
  "created_at": "2025-01-15T10:00:00Z",
  "updated_at": "2025-01-16T14:30:00Z",
  "version": 3
}
```

#### 4. 伏笔追踪 (continuity/foreshadowing.json)

```json
{
  "foreshadowing_items": [
    {
      "id": "fsh-001",
      "type": "object",
      "description": "神秘玉佩",
      "planted": {
        "chapter": 3,
        "line": "玉佩在月光下微微发光",
        "subtlety": "medium"
      },
      "payoff": {
        "planned_chapter": 50,
        "actual_chapter": null,
        "description": "玉佩是母亲留下的定位信物"
      },
      "status": "planted",
      "reminders": [15, 30, 45]
    },
    {
      "id": "fsh-002",
      "type": "character",
      "description": "神秘老者的真实身份",
      "planted": {
        "chapter": 7,
        "line": "老者看着主角的眼神意味深长",
        "subtlety": "high"
      },
      "payoff": {
        "planned_chapter": 30,
        "actual_chapter": 32,
        "description": "老者是主角外公"
      },
      "status": "resolved"
    }
  ],
  "statistics": {
    "total": 25,
    "planted": 18,
    "resolved": 7,
    "overdue": 2
  }
}
```

### 数据访问模式

#### 读取优先级

```
撰写第N章时的数据加载顺序：

必须加载（总计约2000 tokens）：
├── 1. 第N章大纲                    ~300 tokens
├── 2. 涉及角色的精简档案            ~500 tokens
├── 3. 相关设定摘要                  ~300 tokens
└── 4. 前一章摘要                    ~400 tokens

按需加载：
├── 5. 相关伏笔列表                  ~200 tokens
├── 6. 角色当前状态快照              ~200 tokens
├── 7. 前2-5章摘要                   ~800 tokens
└── 8. 详细设定（仅首次涉及时）       ~500 tokens
```

#### 数据更新触发

| 事件 | 更新的数据文件 |
|------|---------------|
| 完成一章 | ch-meta.json, summary.md, timeline.json, character-states.json |
| 新增角色 | characters/index.json, [character].json |
| 扩展设定 | world-bible.json, 相关子文件 |
| 埋设伏笔 | foreshadowing.json, ch-meta.json |
| 回收伏笔 | foreshadowing.json |
| 角色状态变化 | character-states.json, [character].json |

---

## 上下文管理策略

> **v1.1新增**：解决数十万字内容超出上下文窗口的问题

### 分层摘要机制

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           分层摘要体系                                   │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│   全书摘要 (1000字)                                                      │
│   └── 卷摘要 (每卷500字)                                                 │
│       └── 弧摘要 (每个故事弧300字)                                       │
│           └── 章节摘要 (每章100-200字)                                   │
│               └── 章节正文 (每章3000字)                                  │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

#### 章节摘要模板

```markdown
## 第X章摘要

**时间**：[故事时间]
**地点**：[主要场景]
**POV**：[视角角色]

**事件**：
- [核心事件1]
- [核心事件2]

**角色变化**：
- [角色A]：[状态变化]

**伏笔**：
- 埋设：[描述]
- 回收：[描述]

**章末状态**：[简述结束时的情况]
```

#### 卷摘要模板

```markdown
## 第X卷摘要：[卷名]

**时间跨度**：[起止时间]
**核心冲突**：[本卷主要矛盾]

**主线进展**：
- [进展1]
- [进展2]

**角色发展**：
- [主角]：[从A状态到B状态]
- [重要配角]：[发展]

**关键转折**：
1. 第X章：[转折点]
2. 第Y章：[转折点]

**未解决问题**：
- [悬念1]
- [悬念2]
```

### 上下文预算分配

#### 标准写作会话（假设8K可用tokens）

```
┌─────────────────────────────────────────────────────────────────────────┐
│  上下文分配                                                              │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  [系统指令 + Skill内容]     1500 tokens  ████████                       │
│  [章节大纲]                  300 tokens  ██                             │
│  [角色档案(精简)]            500 tokens  ███                            │
│  [前章摘要]                  400 tokens  ██                             │
│  [相关设定]                  300 tokens  ██                             │
│  [当前对话]                  500 tokens  ███                            │
│  ─────────────────────────────────────                                  │
│  [生成预留]                 4500 tokens  ██████████████████████         │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

#### 审阅会话（需要更多上下文）

```
┌─────────────────────────────────────────────────────────────────────────┐
│  审阅上下文分配                                                          │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  [系统指令 + Skill内容]     1000 tokens  █████                          │
│  [待审阅章节全文]           3000 tokens  ███████████████                │
│  [角色档案]                  500 tokens  ███                            │
│  [一致性检查清单]            300 tokens  ██                             │
│  [前文相关摘要]              700 tokens  ████                           │
│  ─────────────────────────────────────                                  │
│  [分析输出预留]             2500 tokens  █████████████                  │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 检索策略

#### 按需检索触发条件

| 触发场景 | 检索内容 | 检索方式 |
|---------|---------|----------|
| 提及特定角色 | 该角色完整档案 | ID精确查询 |
| 涉及历史事件 | 相关时间线片段 | 时间范围查询 |
| 使用专有术语 | 术语定义 | 关键词查询 |
| 回收伏笔 | 埋设时的原文 | 伏笔ID查询 |
| 场景发生地 | 地点详细设定 | 地名查询 |

#### 检索接口规格

```python
# content-indexing Skill 提供的检索接口

def search_chapters(query: str, scope: str = "all") -> List[SearchResult]:
    """
    搜索章节内容

    Args:
        query: 搜索关键词
        scope: "all" | "volume-N" | "chapter-range:M-N"

    Returns:
        匹配的章节片段列表，每个包含：
        - chapter_id: 章节标识
        - snippet: 匹配片段（前后各50字）
        - relevance_score: 相关度分数
    """

def get_character_state(char_id: str, at_chapter: int) -> CharacterState:
    """
    获取角色在指定章节时的状态

    Returns:
        location, emotional_state, power_level, relationships等
    """

def get_active_foreshadowing(current_chapter: int) -> List[Foreshadowing]:
    """
    获取当前应注意的伏笔

    Returns:
        已埋设但未回收的伏笔列表，按紧急程度排序
    """
```

---

## 架构设计

### 系统架构图

```
                         ┌─────────────────────────────────────┐
                         │         novel-project               │
                         │      （项目管理与状态查询）           │
                         └──────────────┬──────────────────────┘
                                        │
           ┌─────────────────┬──────────┴──────────┬─────────────────┐
           │                 │                     │                 │
           ▼                 ▼                     ▼                 ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│  worldbuilding  │ │ plot-architecting│ │character-managing│ │ content-indexing│
│  (世界观构建)    │ │   (剧情规划)     │ │   (角色管理)     │ │  (内容检索)     │
└────────┬────────┘ └────────┬────────┘ └────────┬────────┘ └────────┬────────┘
         │                   │                   │                   │
         └───────────────────┴─────────┬─────────┴───────────────────┘
                                       │
                            ┌──────────┴──────────┐
                            │   prose-crafting    │
                            │    (文风与写作)      │
                            └──────────┬──────────┘
                                       │
                     ┌─────────────────┴─────────────────┐
                     │                                   │
                     ▼                                   ▼
          ┌─────────────────────┐           ┌─────────────────────┐
          │ continuity-tracking │           │ manuscript-reviewing│
          │  (一致性追踪)        │           │   (稿件审阅)        │
          └─────────────────────┘           └─────────────────────┘

                                    │
                     ┌──────────────┴──────────────┐
                     │      数据层 (Data Layer)     │
                     │  world/ characters/ chapters/ │
                     │  continuity/ glossary/ config/ │
                     └─────────────────────────────┘
```

### Skill职责矩阵（v1.1明确边界）

| Skill | 核心职责 | 明确边界 | 不负责 |
|-------|---------|---------|--------|
| `worldbuilding` | 创建/扩展世界设定 | 设定的创建与记录 | 使用中的一致性检查（由continuity负责） |
| `character-managing` | 管理角色档案与关系 | 角色信息的CRUD | 角色在章节中的具体表现（由prose负责） |
| `plot-architecting` | 设计故事结构与大纲 | 宏观剧情规划 | 具体章节写作（由prose负责） |
| `prose-crafting` | 撰写正文内容 | 文字创作 | 逻辑检查（由reviewing负责） |
| `continuity-tracking` | 事实一致性追踪 | 客观事实的一致 | 叙事合理性（由reviewing负责） |
| `content-indexing` | 内容检索与摘要 | 信息查找 | 内容创建 |
| `manuscript-reviewing` | 质量审阅与修订建议 | 逻辑/节奏/表达 | 事实一致性（由continuity负责） |
| `novel-project` | 进度查询与阶段建议 | 状态汇总 | 具体创作工作 |

### 目录结构

```
novel-skills/
│
├── worldbuilding/                 # 世界观构建
│   ├── SKILL.md                   # 核心指令（<300行）
│   ├── GEOGRAPHY.md               # 地理设定方法论
│   ├── HISTORY.md                 # 历史构建指南
│   ├── POWER-SYSTEM.md            # 力量体系设计
│   ├── SOCIETY.md                 # 社会结构设定
│   └── templates/
│       ├── world-bible-schema.json    # 世界圣经结构定义
│       └── setting-card-template.md   # 设定卡片模板
│
├── character-managing/            # 角色管理
│   ├── SKILL.md
│   ├── RELATIONSHIP.md            # 关系网络管理
│   ├── CHARACTER-ARC.md           # 角色弧光设计
│   ├── DIALOGUE-VOICE.md          # 角色语言风格
│   └── templates/
│       ├── character-schema.json      # 角色档案结构
│       └── relationship-types.json    # 关系类型定义
│
├── plot-architecting/             # 剧情规划
│   ├── SKILL.md
│   ├── STRUCTURE.md               # 故事结构理论
│   ├── CONFLICT.md                # 冲突设计方法
│   ├── PACING.md                  # 节奏控制指南
│   └── templates/
│       ├── outline-schema.json        # 大纲结构定义
│       └── chapter-plan-template.md   # 章节计划模板
│
├── prose-crafting/                # 文风控制与写作
│   ├── SKILL.md
│   ├── DIALOGUE.md                # 对话写作技巧
│   ├── DESCRIPTION.md             # 描写技法
│   ├── POV.md                     # 视角控制
│   ├── SCENE-TYPES.md             # 场景类型写作要点
│   └── styles/
│       ├── wuxia-style.md             # 武侠风格样本
│       ├── modern-style.md            # 现代都市风格
│       ├── romance-style.md           # 言情风格样本
│       └── style-parameters.json      # 风格参数定义
│
├── continuity-tracking/           # 连续性追踪
│   ├── SKILL.md
│   ├── TIMELINE.md                # 时间线管理方法
│   ├── FACT-CHECKING.md           # 事实核查清单
│   ├── FORESHADOWING.md           # 伏笔管理指南
│   └── checklists/
│       ├── character-consistency.md   # 角色一致性检查
│       ├── world-consistency.md       # 设定一致性检查
│       └── timeline-consistency.md    # 时间线一致性检查
│
├── content-indexing/              # 内容检索（v1.1新增）
│   ├── SKILL.md
│   ├── SEARCH-PATTERNS.md         # 检索模式指南
│   ├── SUMMARY-GENERATION.md      # 摘要生成规范
│   └── scripts/
│       ├── search_interface.py        # 检索接口定义
│       └── summary_templates.py       # 摘要模板
│
├── manuscript-reviewing/          # 稿件审阅
│   ├── SKILL.md
│   ├── LOGIC-CHECK.md             # 逻辑检查方法
│   ├── PACING-ANALYSIS.md         # 节奏分析
│   ├── POLISH.md                  # 润色指南
│   └── checklists/
│       ├── chapter-review.md          # 章节审阅清单
│       ├── character-review.md        # 角色表现审阅
│       └── prose-review.md            # 文字质量审阅
│
└── novel-project/                 # 项目管理
    ├── SKILL.md
    ├── WORKFLOW.md                # 工作流程定义
    ├── PHASE-GUIDE.md             # 阶段指引
    └── templates/
        ├── project-config-schema.json # 项目配置结构
        └── progress-report.md         # 进度报告模板
```

### Skill元数据汇总（v1.1优化触发词）

```yaml
# worldbuilding
---
name: worldbuilding
description: |
  构建和管理小说世界观设定，包括地理、历史、社会结构、力量体系。
  触发词：世界观、设定、地理、历史、修炼体系、魔法系统、势力、宗门、地图。
  在创建新世界、扩展设定或查询已有设定时使用。
---

# character-managing
---
name: character-managing
description: |
  管理小说角色档案、追踪关系网络和成长弧线。
  触发词：角色、人物、主角、配角、反派、关系、人设、性格、背景。
  在创建角色、查询角色信息、分析角色关系或设计角色发展时使用。
---

# plot-architecting
---
name: plot-architecting
description: |
  设计故事结构、规划剧情线和章节大纲。
  触发词：剧情、大纲、结构、章节规划、冲突、高潮、转折、主线、支线。
  在构思故事框架、设计冲突、规划章节或调整剧情时使用。
---

# prose-crafting
---
name: prose-crafting
description: |
  控制写作风格，撰写正文内容，处理对话和描写。
  触发词：写、撰写、正文、文风、风格、对话、描写、场景、视角。
  在撰写章节正文、调整文风或创作特定场景时使用。
---

# continuity-tracking
---
name: continuity-tracking
description: |
  追踪故事时间线、检查事实一致性、管理伏笔。
  触发词：时间线、一致性、矛盾、伏笔、前后不一、连续性、事实核查。
  在检查内容一致性、管理伏笔或验证时间线时使用。
---

# content-indexing
---
name: content-indexing
description: |
  检索已写内容、生成摘要、查找特定信息。
  触发词：搜索、查找、在哪里、之前写过、回顾、摘要、前文。
  在需要查找前文内容、生成摘要或检索特定信息时使用。
---

# manuscript-reviewing
---
name: manuscript-reviewing
description: |
  审阅稿件质量，检查逻辑漏洞，分析节奏，提供润色建议。
  触发词：审阅、检查、修改、润色、问题、逻辑、节奏、优化。
  在完成章节后进行质量检查或需要修订建议时使用。
---

# novel-project
---
name: novel-project
description: |
  查询项目状态、追踪进度、提供阶段建议。
  触发词：进度、状态、完成了多少、接下来、计划、里程碑、统计。
  在查询项目进度、获取阶段建议或查看统计信息时使用。
---
```

---

## 核心Skill规格

### 1. worldbuilding - 世界观构建

#### 职责边界

```
✅ 负责：                          ❌ 不负责：
├── 创建世界设定                    ├── 写作中的设定引用（prose-crafting）
├── 扩展已有设定                    ├── 设定使用的一致性检查（continuity-tracking）
├── 记录设定到数据文件              └── 角色背景（character-managing）
├── 查询设定内容
└── 设定创建时的自洽验证
```

#### 关键工作流

**创建新设定**：
```
1. 确认设定类型（地理/历史/社会/力量）
2. 检查是否与已有设定冲突
3. 生成设定内容
4. 验证内在逻辑
5. 写入对应数据文件
6. 更新world-bible.json索引
```

**扩展已有设定**：
```
1. 读取相关已有设定
2. 确认扩展方向
3. 生成扩展内容（保持一致）
4. 验证与原设定兼容
5. 更新数据文件
```

#### 与其他Skill协作

| 场景 | 协作Skill | 数据流向 |
|------|-----------|----------|
| 角色需要背景 | → character-managing | 提供世界背景供角色设定使用 |
| 剧情涉及新地点 | ← plot-architecting | 根据剧情需要创建地点设定 |
| 检查设定一致性 | → continuity-tracking | 提供设定数据供一致性检查 |

---

### 2. character-managing - 角色管理

#### 职责边界

```
✅ 负责：                          ❌ 不负责：
├── 创建角色档案                    ├── 角色在章节中的具体表现（prose-crafting）
├── 管理角色关系网络                ├── 角色出场的一致性检查（continuity-tracking）
├── 设计角色弧线                    └── 角色相关的剧情线（plot-architecting）
├── 定义角色语言风格
├── 更新角色状态
└── 查询角色信息
```

#### 角色状态管理

```json
{
  "state_update_triggers": {
    "chapter_complete": "更新角色所在位置、情绪状态",
    "power_change": "更新力量等级、新获得能力",
    "relationship_change": "更新关系网络",
    "injury_or_recovery": "更新身体状态"
  }
}
```

#### 与其他Skill协作

| 场景 | 协作Skill | 数据流向 |
|------|-----------|----------|
| 写作需要角色信息 | → prose-crafting | 提供角色档案和语言风格 |
| 剧情涉及角色发展 | ↔ plot-architecting | 双向：弧线影响剧情，剧情触发弧线 |
| 角色一致性检查 | → continuity-tracking | 提供角色档案供检查 |

---

### 3. plot-architecting - 剧情规划

#### 职责边界

```
✅ 负责：                          ❌ 不负责：
├── 设计整体故事结构                ├── 撰写正文（prose-crafting）
├── 规划章节大纲                    ├── 一致性检查（continuity-tracking）
├── 管理主线/支线                   └── 质量审阅（manuscript-reviewing）
├── 设计冲突与转折
├── 控制宏观节奏
└── 调整剧情走向
```

#### 大纲层级

```
故事结构
└── 卷大纲
    └── 弧大纲（故事弧）
        └── 章节大纲
            ├── 场景1
            ├── 场景2
            └── 章末钩子
```

#### 章节大纲标准格式

```markdown
## 第N章：[章节标题]

### 元信息
- **卷/弧**：第X卷 / [弧名称]
- **故事时间**：[时间点]
- **POV角色**：[视角人物]
- **字数目标**：3000字

### 章节目标
- 主要目标：[推进什么]
- 次要目标：[顺带完成什么]

### 场景分解
1. **场景1**：[地点]
   - 事件：[发生什么]
   - 涉及角色：[角色列表]
   - 情绪基调：[基调]

2. **场景2**：[地点]
   - 事件：[发生什么]
   - 涉及角色：[角色列表]
   - 情绪基调：[基调]

### 伏笔操作
- 埋设：[如有]
- 回收：[如有]

### 章末钩子
[悬念设置]

### 注意事项
- [需要注意的连续性问题]
- [角色当前状态提醒]
```

---

### 4. prose-crafting - 文风控制与写作

#### 职责边界

```
✅ 负责：                          ❌ 不负责：
├── 撰写章节正文                    ├── 剧情规划（plot-architecting）
├── 控制文字风格                    ├── 逻辑检查（manuscript-reviewing）
├── 处理对话和描写                  ├── 一致性检查（continuity-tracking）
├── 场景氛围营造                    └── 角色档案管理（character-managing）
└── 视角控制
```

#### 风格参数定义

```json
{
  "style_parameters": {
    "tone": {
      "type": "enum",
      "options": ["轻松", "沉稳", "热血", "压抑", "诙谐", "冷峻"],
      "description": "整体情感基调"
    },
    "vocabulary": {
      "type": "enum",
      "options": ["口语化", "书面化", "古风", "现代", "混合"],
      "description": "用词风格"
    },
    "sentence_length": {
      "type": "enum",
      "options": ["短句为主", "长句为主", "混合", "节奏变化"],
      "description": "句式偏好"
    },
    "description_density": {
      "type": "float",
      "range": [0.2, 0.8],
      "description": "描写密度，0.2极简，0.8细腻"
    },
    "dialogue_ratio": {
      "type": "float",
      "range": [0.2, 0.7],
      "description": "对话占比"
    },
    "pacing": {
      "type": "enum",
      "options": ["快节奏", "慢节奏", "张弛有度"],
      "description": "叙事节奏"
    }
  }
}
```

#### 场景类型写作指南

| 场景类型 | 句式 | 描写重点 | 节奏 | 技巧 |
|---------|------|---------|------|------|
| 战斗/动作 | 短句为主 | 动作、速度 | 快 | 动词有力，留白，画面感 |
| 情感/对话 | 混合 | 心理、表情 | 慢 | 潜台词，环境烘托 |
| 日常/过渡 | 自然 | 细节、氛围 | 中 | 轻松，角色个性 |
| 高潮/转折 | 变化 | 张力、情绪 | 先慢后快 | 铺垫，爆发，余韵 |
| 描写/说明 | 长句 | 画面、感官 | 慢 | 多感官，比喻 |

---

### 5. continuity-tracking - 连续性追踪

#### 职责边界

```
✅ 负责：                          ❌ 不负责：
├── 时间线管理                      ├── 叙事合理性（manuscript-reviewing）
├── 事实一致性检查                  ├── 文字质量（manuscript-reviewing）
├── 伏笔追踪                        └── 剧情逻辑（plot-architecting）
├── 角色状态追踪
└── 设定使用一致性
```

#### 一致性检查类型

```yaml
fact_consistency:  # 事实一致性
  - 人名/地名拼写
  - 角色年龄
  - 角色外貌描述
  - 地理位置关系
  - 力量等级
  - 物品持有

timeline_consistency:  # 时间线一致性
  - 事件顺序
  - 时间跨度
  - 日夜/季节
  - 年龄变化

state_consistency:  # 状态一致性
  - 角色所在位置
  - 角色伤势
  - 角色情绪
  - 关系状态
```

#### 伏笔状态机

```
[构思] → [埋设] → [强化(可选)] → [回收] → [完结]
   │        │           │           │
   │        │           │           └── 伏笔已解决
   │        │           └── 在后续章节中再次暗示
   │        └── 在某章节中埋下伏笔
   └── 计划中的伏笔

状态追踪：
- planted_chapter: 埋设章节
- reinforced_chapters: [强化章节列表]
- resolved_chapter: 回收章节
- urgency: 距离计划回收的章节数
```

---

### 6. content-indexing - 内容检索（v1.1新增）

#### 职责范围

```
✅ 负责：                          ❌ 不负责：
├── 搜索已写内容                    ├── 内容创建（各专业Skill）
├── 生成章节摘要                    ├── 质量判断（manuscript-reviewing）
├── 查询角色出场                    └── 一致性判断（continuity-tracking）
├── 检索特定情节
└── 汇总统计信息
```

#### 核心功能

**1. 内容搜索**
```
输入：关键词/短语
输出：匹配的章节列表，包含：
  - 章节ID
  - 匹配片段（高亮）
  - 上下文摘要
  - 相关度评分
```

**2. 摘要生成**
```
输入：章节内容
输出：结构化摘要，包含：
  - 事件摘要（100字）
  - 角色状态变化
  - 伏笔操作
  - 关键对话/场景
```

**3. 角色出场检索**
```
输入：角色ID
输出：出场章节列表，包含：
  - 章节ID
  - 出场类型（主要/次要/提及）
  - 该章中的关键行为
```

---

### 7. manuscript-reviewing - 稿件审阅

#### 职责边界

```
✅ 负责：                          ❌ 不负责：
├── 逻辑合理性检查                  ├── 事实一致性（continuity-tracking）
├── 节奏分析                        ├── 内容创作（prose-crafting）
├── 文字润色建议                    └── 剧情调整（plot-architecting）
├── 角色行为合理性
└── 读者体验评估
```

#### 审阅维度

```yaml
logic_review:  # 逻辑审阅
  - 角色行为动机是否充分
  - 事件因果是否合理
  - 冲突解决是否自洽

pacing_review:  # 节奏审阅
  - 场景长度是否均衡
  - 张力曲线是否合理
  - 是否有拖沓/仓促

prose_review:  # 文字审阅
  - 是否有重复用词
  - 句式是否单调
  - 描写是否恰当

character_review:  # 角色表现审阅
  - 对话是否符合人设
  - 情感变化是否有铺垫
  - 角色弧线是否推进
```

#### 问题报告格式

```markdown
## 审阅报告：第X章

### 总体评价
[一句话总结]

### 问题列表

#### 逻辑问题
1. **[严重]** 第3段：主角前文说不会游泳，此处却游过河流
   - 位置：第3段第2句
   - 建议：修改为借助工具过河，或前文补充学会游泳的情节

#### 节奏问题
1. **[建议]** 战斗场景过长（约1500字），建议压缩至1000字
   - 位置：第5-8段
   - 建议：删减重复的招式描写

#### 文字问题
1. **[轻微]** "缓缓"一词在本章出现7次
   - 建议：替换为"慢慢"、"徐徐"等同义词

### 亮点
- [值得保留的优秀段落]

### 修订优先级
1. 逻辑问题#1（必须修复）
2. 节奏问题#1（建议修复）
3. 文字问题#1（可选优化）
```

---

### 8. novel-project - 项目管理

#### 职责边界

```
✅ 负责：                          ❌ 不负责：
├── 项目状态查询                    ├── 具体创作工作（各专业Skill）
├── 进度统计                        ├── 质量判断（manuscript-reviewing）
├── 阶段建议                        └── 内容检索（content-indexing）
├── 里程碑追踪
└── 工作流建议
```

#### 状态查询接口

```markdown
## 可查询的状态

### 进度统计
- 总字数 / 目标字数 / 完成比例
- 已完成章节数 / 计划章节数
- 当前所处阶段（构思/规划/写作/修订）

### 质量状态
- 待审阅章节数
- 未解决问题数
- 待回收伏笔数（按紧急度）

### 近期活动
- 最近完成的章节
- 最近更新的设定
- 最近创建的角色

### 阶段建议
- 当前阶段的推荐工作流
- 下一步建议操作
- 需要注意的事项
```

---

## Skill协作工作流

### 创作阶段工作流（v1.1优化）

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          长篇小说创作工作流 v1.1                             │
└─────────────────────────────────────────────────────────────────────────────┘

阶段一：构思期
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│  novel-project        worldbuilding       character-managing               │
│  (初始化项目)    →    (构建世界观)    →   (创建核心角色)                    │
│       │                    │                    │                          │
│       ▼                    ▼                    ▼                          │
│  config/project.json  world/*.json         characters/*.json               │
│                                                                             │
│  输出：项目配置、世界圣经、核心角色档案                                       │
│  里程碑：✓ 项目初始化完成                                                    │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
阶段二：规划期
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│  plot-architecting  →  character-managing  →  continuity-tracking          │
│  (设计故事结构)         (完善角色弧线)         (建立追踪基线)                │
│       │                      │                      │                      │
│       ▼                      ▼                      ▼                      │
│  plot/structure.json   characters/*.json     continuity/timeline.json      │
│  plot/outline/*.json   (更新arc字段)         continuity/foreshadowing.json │
│                                                                             │
│  输出：故事结构、章节大纲、角色弧线、时间线框架、伏笔计划                      │
│  里程碑：✓ 大纲完成                                                          │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
阶段三：写作期（循环）
┌─────────────────────────────────────────────────────────────────────────────┐
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │  每章节循环：                                                          │  │
│  │                                                                       │  │
│  │  content-indexing  →  prose-crafting  →  continuity-tracking         │  │
│  │  (加载前文上下文)      (撰写正文)         (一致性检查)                 │  │
│  │        │                   │                   │                      │  │
│  │        │                   ▼                   │                      │  │
│  │        │           chapters/ch-N.md            │                      │  │
│  │        │                   │                   │                      │  │
│  │        │                   ▼                   ▼                      │  │
│  │        │           manuscript-reviewing  ←────┘                       │  │
│  │        │           (质量审阅)                                         │  │
│  │        │                   │                                          │  │
│  │        │         ┌────────┴────────┐                                  │  │
│  │        │         ▼                 ▼                                  │  │
│  │        │     [通过]            [不通过]                                │  │
│  │        │         │                 │                                  │  │
│  │        │         ▼                 ▼                                  │  │
│  │        │   content-indexing   prose-crafting                          │  │
│  │        │   (生成摘要,更新索引)  (修订) → 返回审阅                       │  │
│  │        │         │                                                    │  │
│  │        │         ▼                                                    │  │
│  │        └───→ novel-project                                            │  │
│  │              (更新进度)                                                │  │
│  │                                                                       │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
│  每章节产出：正文、摘要、元数据更新、进度更新                                 │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
阶段四：修订期
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│  content-indexing  →  manuscript-reviewing  →  continuity-tracking         │
│  (全稿检索支持)        (全稿审阅)              (全局一致性检查)              │
│                            │                         │                     │
│                            ▼                         ▼                     │
│                      问题清单汇总                一致性报告                 │
│                            │                         │                     │
│                            └───────────┬─────────────┘                     │
│                                        ▼                                   │
│                                prose-crafting                              │
│                                (统一修订润色)                               │
│                                        │                                   │
│                                        ▼                                   │
│                              chapters/*.md (更新)                          │
│                                                                             │
│  输出：修订后终稿、一致性报告、版本快照                                       │
│  里程碑：✓ 终稿完成                                                          │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 单章节写作流程（v1.1详细版）

```markdown
## 单章节写作流程

### 准备阶段
- [ ] 1. 从plot-architecting获取本章大纲
- [ ] 2. 从content-indexing加载前文上下文
      - 前一章摘要
      - 涉及角色当前状态
      - 相关设定摘要
- [ ] 3. 从continuity-tracking获取
      - 待回收伏笔（如有）
      - 需注意的一致性事项

### 写作阶段
- [ ] 4. 使用prose-crafting撰写正文
      - 按场景分段撰写
      - 遵循风格参数
      - 注意角色语言风格

### 检查阶段
- [ ] 5. continuity-tracking一致性检查
      - 事实一致性
      - 时间线一致性
      - 角色状态一致性
- [ ] 6. manuscript-reviewing质量审阅
      - 逻辑合理性
      - 节奏分析
      - 文字质量

### 修订阶段（如需）
- [ ] 7. 根据审阅意见修订
- [ ] 8. 重新检查（返回步骤5）

### 完成阶段
- [ ] 9. content-indexing生成章节摘要
- [ ] 10. 更新数据文件
       - chapters/ch-N.md（正文）
       - chapters/ch-N-meta.json（元数据）
       - chapters/ch-N-summary.md（摘要）
       - continuity/timeline.json（时间线）
       - continuity/character-states.json（角色状态）
- [ ] 11. novel-project更新进度
```

### 异常处理流程（v1.1新增）

#### 写作中断恢复

```markdown
## 中断恢复流程

1. 查询novel-project获取当前状态
   - 最后完成的章节
   - 进行中的章节（如有）

2. 如有进行中的章节：
   - 读取已保存的草稿（如有）
   - 从content-indexing加载上下文
   - 从中断处继续

3. 如无进行中章节：
   - 确认下一章大纲
   - 开始新章节流程
```

#### 一致性检查失败

```markdown
## 一致性问题处理流程

1. continuity-tracking报告问题
   - 问题类型
   - 问题位置
   - 冲突内容

2. 判断问题性质：
   ┌─────────────────────────────────────────┐
   │  当前章节错误？                          │
   │    ├── 是 → 修改当前章节                 │
   │    └── 否 → 前文错误                     │
   │              ├── 可小改 → 修改前文       │
   │              └── 需大改 → 评估影响范围   │
   └─────────────────────────────────────────┘

3. 修改后重新验证
```

#### 审阅不通过

```markdown
## 审阅问题处理流程

1. 按问题严重程度排序：
   - 严重（逻辑硬伤）→ 必须修复
   - 中等（节奏问题）→ 建议修复
   - 轻微（文字优化）→ 可选优化

2. 修订迭代：
   - 修复严重问题
   - 重新审阅
   - 处理中等问题
   - 确认是否继续优化

3. 最多3轮迭代，避免过度修改
```

---

## 通用适配机制

### 类型参数配置（v1.1完善）

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
        "factions": true,
        "magic_rules": true
      },
      "character-managing": {
        "power_tracking": true,
        "relationship_complexity": "medium"
      },
      "plot-architecting": {
        "structure": "升级流",
        "conflict_types": ["实力压制", "资源争夺", "势力对抗"],
        "pacing": "爽点驱动"
      },
      "prose-crafting": {
        "style_preset": "wuxia-style",
        "action_scenes": {
          "frequency": "high",
          "detail_level": "medium"
        },
        "cultivation_scenes": {
          "frequency": "medium",
          "formulaic": true
        }
      },
      "continuity-tracking": {
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
      "character-managing": {
        "emotion_tracking": true,
        "relationship_complexity": "high",
        "inner_monologue": true
      },
      "plot-architecting": {
        "structure": "情感线驱动",
        "conflict_types": ["误会", "身份障碍", "情敌", "家庭反对"],
        "pacing": "情感节奏"
      },
      "prose-crafting": {
        "style_preset": "romance-style",
        "dialogue_heavy": true,
        "emotion_description": "detailed",
        "atmosphere": "important"
      },
      "continuity-tracking": {
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
      "character-managing": {
        "secret_tracking": true,
        "alibi_management": true,
        "motive_tracking": true
      },
      "plot-architecting": {
        "structure": "多线交织",
        "information_control": true,
        "twist_planning": true,
        "fair_play": true
      },
      "prose-crafting": {
        "style_preset": "suspense-style",
        "red_herrings": true,
        "tension_building": true
      },
      "continuity-tracking": {
        "clue_tracking": true,
        "timeline_strict": true,
        "logic_verification": "critical"
      },
      "manuscript-reviewing": {
        "logic_check_level": "exhaustive",
        "reader_deduction_check": true
      }
    }
  }
}
```

---

## 完整SKILL.md示例

### 示例1：worldbuilding/SKILL.md

> 注：以下为独立文件内容，使用四反引号避免嵌套问题

````markdown
---
name: worldbuilding
description: |
  构建和管理小说世界观设定，包括地理、历史、社会结构、力量体系。
  触发词：世界观、设定、地理、历史、修炼体系、魔法系统、势力、宗门、地图。
  在创建新世界、扩展设定或查询已有设定时使用。
---

# 世界观构建

## 快速开始

### 创建新世界

1. 确定世界类型
   - 东方玄幻 / 西方奇幻 / 现代都市 / 未来科幻 / 历史架空

2. 定义核心规则
   ```json
   {
     "power_exists": true,
     "power_type": "灵气修炼",
     "tech_level": "古代",
     "world_scale": "single_world"
   }
   ```

3. 初始化数据文件
   - 创建 `world/world-bible.json`
   - 按需创建子目录

### 查询设定

```
可用查询：
- "查看[地理/历史/势力/力量体系]设定"
- "搜索包含'XX'的设定"
- "查找与'某设定'相关的内容"
```

## 设定管理

### 添加新设定

每个设定记录包含：
- **id**：唯一标识
- **category**：地理/历史/社会/力量
- **name**：名称
- **description**：描述
- **relations**：关联的其他设定

### 扩展已有设定

工作流：
1. 读取相关已有设定
2. 确认扩展不产生冲突
3. 生成扩展内容
4. 更新数据文件

### 设定验证

创建设定时自动检查：
- [ ] 与已有设定无冲突
- [ ] 符合世界核心规则
- [ ] 时间线合理（如涉及历史）

## 详细指南

- **地理设定**：参阅 [GEOGRAPHY.md](GEOGRAPHY.md)
- **历史构建**：参阅 [HISTORY.md](HISTORY.md)
- **力量体系**：参阅 [POWER-SYSTEM.md](POWER-SYSTEM.md)
- **社会结构**：参阅 [SOCIETY.md](SOCIETY.md)

## 数据文件

本Skill管理的数据文件：
- `world/world-bible.json` - 世界圣经主索引
- `world/geography/*.json` - 地理设定
- `world/history/timeline.json` - 历史时间线
- `world/factions/*.json` - 势力组织
- `world/power-system.json` - 力量体系
````

### 示例2：prose-crafting/SKILL.md

````markdown
---
name: prose-crafting
description: |
  控制写作风格，撰写正文内容，处理对话和描写。
  触发词：写、撰写、正文、文风、风格、对话、描写、场景、视角。
  在撰写章节正文、调整文风或创作特定场景时使用。
---

# 文风控制与写作

## 快速开始

### 写作前准备

确认以下信息：
1. 章节大纲（从plot-architecting获取）
2. 涉及角色档案（从character-managing获取）
3. 前文上下文（从content-indexing获取）
4. 当前风格参数

### 风格参数

| 参数 | 当前值 | 可选项 |
|------|--------|--------|
| 基调 | [查询项目配置] | 轻松/沉稳/热血/压抑 |
| 用词 | [查询项目配置] | 口语化/书面化/混合 |
| 句式 | [查询项目配置] | 短句/长句/混合 |
| 描写密度 | [查询项目配置] | 0.2-0.8 |
| 对话比例 | [查询项目配置] | 0.2-0.7 |

## 撰写正文

### 章节写作流程

1. 确认大纲要求
2. 按场景分段撰写
3. 注意角色语言风格
4. 控制章节节奏
5. 设置章末钩子

### 场景写作要点

**战斗场景**：
- 短句为主
- 动词有力
- 节奏紧凑
- 适当留白

**情感场景**：
- 心理描写
- 对话潜台词
- 环境烘托

**日常场景**：
- 对话主导
- 角色个性
- 轻松节奏

## 对话写作

从character-managing获取角色语言风格：
- 口头禅
- 句式习惯
- 用词偏好

**详细指南**：参阅 [DIALOGUE.md](DIALOGUE.md)

## 描写技法

核心原则：
- Show, don't tell
- 多感官描写
- 细节服务整体

**详细指南**：参阅 [DESCRIPTION.md](DESCRIPTION.md)

## 风格样本

- 武侠风格：参阅 [styles/wuxia-style.md](styles/wuxia-style.md)
- 都市风格：参阅 [styles/modern-style.md](styles/modern-style.md)
- 言情风格：参阅 [styles/romance-style.md](styles/romance-style.md)
````

### 示例3：content-indexing/SKILL.md（v1.1新增）

````markdown
---
name: content-indexing
description: |
  检索已写内容、生成摘要、查找特定信息。
  触发词：搜索、查找、在哪里、之前写过、回顾、摘要、前文。
  在需要查找前文内容、生成摘要或检索特定信息时使用。
---

# 内容检索与摘要

## 快速开始

### 搜索内容

```
搜索命令格式：
- "搜索 [关键词]"
- "在第X-Y章中查找 [内容]"
- "查找 [角色名] 的出场章节"
```

### 获取上下文

```
上下文加载：
- "加载第N章的写作上下文"
  → 返回：前章摘要、涉及角色状态、相关设定
```

## 搜索功能

### 全文搜索

输入：关键词或短语
输出：
- 匹配章节列表
- 匹配片段（含上下文）
- 相关度排序

### 角色出场检索

输入：角色ID或名称
输出：
- 出场章节列表
- 出场类型（主要/次要/提及）
- 各章关键行为摘要

### 情节检索

输入：情节描述
输出：
- 相关章节
- 情节发展脉络

## 摘要功能

### 生成章节摘要

输入：章节内容
输出：结构化摘要
- 时间/地点/POV
- 事件摘要（100字）
- 角色状态变化
- 伏笔操作

### 生成卷摘要

输入：卷号
输出：
- 核心冲突
- 主线进展
- 角色发展
- 关键转折

## 上下文加载

### 写作上下文包

为撰写第N章，自动加载：
1. 第N章大纲
2. 第N-1章摘要
3. 涉及角色的当前状态
4. 相关设定摘要
5. 待处理伏笔

### 审阅上下文包

为审阅第N章，自动加载：
1. 第N章全文
2. 角色档案（涉及的）
3. 一致性检查清单
4. 前文相关摘要
````

---

## 评估体系

> **v1.1新增**：提供具体的评估场景和标准

### 评估场景定义

```json
{
  "evaluations": [
    {
      "id": "eval-001",
      "name": "单章写作",
      "description": "从大纲撰写一个完整章节",
      "skills_tested": ["prose-crafting", "character-managing", "content-indexing"],
      "setup": {
        "prerequisite_chapters": 5,
        "chapter_to_write": 6,
        "outline_provided": true
      },
      "input": "按照第6章大纲，撰写一个约3000字的章节",
      "expected_behaviors": [
        "正确加载前文上下文",
        "遵循章节大纲",
        "保持角色语言风格一致",
        "控制在目标字数±10%",
        "设置章末钩子"
      ],
      "success_criteria": {
        "word_count": {"min": 2700, "max": 3300},
        "outline_adherence": "all_scenes_covered",
        "character_voice": "consistent_with_profile",
        "continuity_errors": 0
      }
    },
    {
      "id": "eval-002",
      "name": "一致性检测",
      "description": "发现并报告章节中的一致性问题",
      "skills_tested": ["continuity-tracking", "content-indexing"],
      "setup": {
        "test_chapter": "包含3个故意植入的一致性错误",
        "errors": [
          {"type": "character_appearance", "detail": "眼睛颜色变化"},
          {"type": "timeline", "detail": "时间跳跃不合理"},
          {"type": "power_level", "detail": "能力超出当前等级"}
        ]
      },
      "input": "检查本章的一致性问题",
      "expected_behaviors": [
        "检测到全部3个错误",
        "准确定位错误位置",
        "提供修复建议"
      ],
      "success_criteria": {
        "detection_rate": 1.0,
        "false_positives": {"max": 1},
        "fix_suggestions": "actionable"
      }
    },
    {
      "id": "eval-003",
      "name": "复杂场景写作",
      "description": "撰写包含5个以上角色的群戏场景",
      "skills_tested": ["prose-crafting", "character-managing"],
      "setup": {
        "scene_type": "多角色对话",
        "characters": 6,
        "conflict": "观点分歧"
      },
      "input": "撰写一个6人会议场景，展现不同立场的冲突",
      "expected_behaviors": [
        "每个角色有独特的声音",
        "对话区分度高",
        "冲突清晰呈现",
        "场景节奏合理"
      ],
      "success_criteria": {
        "voice_distinction": "each_character_recognizable",
        "dialogue_attribution": "clear_without_tags",
        "conflict_resolution": "logical"
      }
    },
    {
      "id": "eval-004",
      "name": "伏笔回收",
      "description": "自然地回收之前埋设的伏笔",
      "skills_tested": ["prose-crafting", "continuity-tracking", "content-indexing"],
      "setup": {
        "foreshadowing": {
          "id": "fsh-test",
          "planted_chapter": 3,
          "hint": "神秘玉佩在月光下发光",
          "payoff": "玉佩是定位信物"
        },
        "current_chapter": 50
      },
      "input": "在本章回收神秘玉佩的伏笔",
      "expected_behaviors": [
        "检索到原始伏笔内容",
        "自然融入当前剧情",
        "呼应原始暗示",
        "更新伏笔状态为已回收"
      ],
      "success_criteria": {
        "original_reference": "included",
        "integration": "natural",
        "data_update": "foreshadowing.json_updated"
      }
    }
  ]
}
```

### 评估执行清单

```markdown
## 评估执行步骤

### 准备阶段
- [ ] 创建测试项目数据
- [ ] 准备评估输入
- [ ] 记录初始状态

### 执行阶段
- [ ] 运行评估场景
- [ ] 记录Skill调用序列
- [ ] 记录输出结果

### 验证阶段
- [ ] 对照success_criteria检查
- [ ] 记录通过/失败
- [ ] 分析失败原因

### 迭代阶段
- [ ] 根据失败调整Skill
- [ ] 重新运行失败场景
- [ ] 直到全部通过
```

---

## 实施指南

### 部署步骤（v1.1更新）

#### 第一阶段：基础设施

```bash
# 1. 创建Skill目录结构
mkdir -p novel-skills/{worldbuilding,character-managing,plot-architecting,prose-crafting,continuity-tracking,content-indexing,manuscript-reviewing,novel-project}/{templates,scripts,styles,checklists}

# 2. 创建数据目录结构
mkdir -p novel-project-data/{config,world/{geography,history,factions},characters/{main,supporting},plot/outline,chapters,continuity,glossary,progress/versions}

# 3. 初始化核心文件
touch novel-skills/*/SKILL.md
touch novel-project-data/config/project.json
```

#### 第二阶段：核心Skill

1. 创建8个SKILL.md（使用本文档示例）
2. 创建关键模板文件
3. 定义数据结构schema

#### 第三阶段：测试验证

1. 运行评估场景
2. 验证Skill触发准确性
3. 测试数据持久化
4. 验证协作工作流

### 迭代优化建议

#### 监控指标

| 指标 | 目标 | 说明 |
|------|------|------|
| Skill触发准确率 | >90% | 用户意图与触发Skill匹配 |
| 一致性错误率 | <5% | 生成内容的一致性问题 |
| 上下文加载成功率 | >95% | 正确加载所需上下文 |
| 用户满意度 | >80% | 输出质量满足期望 |

#### 常见问题处理

| 问题 | 可能原因 | 解决方案 |
|------|---------|----------|
| Skill未触发 | description触发词不足 | 增加触发词覆盖 |
| 错误Skill触发 | 职责边界模糊 | 明确边界，调整description |
| 上下文不足 | 加载策略不当 | 调整上下文预算分配 |
| 一致性错误 | 数据未及时更新 | 强化数据更新触发 |

### 使用建议

```
项目阶段           推荐Skill组合
─────────────────────────────────────────────
构思期            novel-project + worldbuilding + character-managing
规划期            plot-architecting + character-managing + continuity-tracking
写作期            prose-crafting + content-indexing + continuity-tracking
审阅期            manuscript-reviewing + continuity-tracking + content-indexing
修订期            prose-crafting + manuscript-reviewing
```

---

## 附录

### A. 数据文件Schema索引

| 文件 | Schema位置 | 说明 |
|------|-----------|------|
| project.json | 本文档"数据管理架构"节 | 项目配置 |
| [character].json | 本文档"数据管理架构"节 | 角色档案 |
| ch-meta.json | 本文档"数据管理架构"节 | 章节元数据 |
| foreshadowing.json | 本文档"数据管理架构"节 | 伏笔追踪 |
| genre_configs | 本文档"通用适配机制"节 | 类型配置 |
| style_parameters | prose-crafting规格节 | 风格参数 |

### B. Skill文件清单

| 路径 | 类型 | 行数限制 |
|------|------|---------|
| `*/SKILL.md` | 核心指令 | <300行 |
| `*/*.md`（非SKILL） | 详细指南 | <500行 |
| `*/templates/*.json` | 数据模板 | 无限制 |
| `*/checklists/*.md` | 检查清单 | <200行 |
| `*/styles/*.md` | 风格样本 | <300行 |

### C. 版本兼容性

| 版本 | 兼容性 | 迁移说明 |
|------|--------|---------|
| v1.0 → v1.1 | 需迁移 | 需创建content-indexing Skill，重构数据目录 |

---

*文档版本：1.1*
*更新日期：2025-12*
*设计依据：Anthropic Agent Skills 最佳实践*
