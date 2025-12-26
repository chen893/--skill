# 小说skills最终方案-gpt

面向“数十万字长篇（尤其是连载型）”创作与管理：既要**写得快**（起点节奏/爽点/钩子），又要**写得稳**（设定一致、伏笔可回收、可回滚）。

---

## 1) 方案 A vs 方案 B：深度对比（优缺点）

| 维度 | 方案 A：`docs/novel-skills-system-claude.md`（规格 v1.1）优点 | 方案 A 缺点 | 方案 B：`docs/novel-skills-system-gpt.md`（GPT 设计）优点 | 方案 B 缺点 |
|---|---|---|---|---|
| 核心取向 | **工程规格书**思路：数据层 + 上下文策略 + Skill 边界 + 评估体系，一套“可验证”的长期系统 | 容易“过度工程化”，写作者日常维护成本高，创作流可能被打断 | **写作运营手册**思路：工作区结构 + 操作协议 + 最小闭环，强调“能持续写下去” | 规范偏“人为纪律”，缺少强结构与自动化时，后期容易跑偏 |
| Skill 组织方式 | 8 个核心 Skill，配**职责矩阵**明确“不负责什么”，降低技能互踩 | 缺少“总控/路由”层时，复杂请求可能出现并行拉扯（多个 Skill 争夺主导） | 明确提出 `novel-orchestrating` 总控 Skill（分流/调度/推进状态） | 总控若写得过强，会变成“万能 Skill”，吞并其他职责（反而回到提示墙） |
| 数据持久化模型 | 提供 `novel-project-data/` 的**结构化数据仓库**（JSON），跨会话稳定、可脚本化校验 | 结构化文件多、字段多：不配套自动化工具时，维护会变成负担；一旦不更新数据层就会失真 | 以 `novel/` 为核心的**人类可读知识库**（Markdown），更符合写作心智 | 仅用 Markdown 时，“可计算性”弱：检索、统计、影响分析、批量校验会越来越难 |
| 上下文管理 | 明确**分层摘要 + 上下文预算分配 + 检索触发条件**；写作/审阅会话有不同策略 | 预算示例更偏某模型窗口假设（如 8K），跨模型/长上下文需要二次适配 | 明确“先小后大”的**默认阅读顺序**（state→bible→scene-cards→章节摘要→必要时回读正文） | 缺少量化预算/检索接口时，遇到复杂问题仍可能“回读过量” |
| 检索/索引能力 | 定义 `content-indexing` 的检索接口（如 `search_chapters(...)`），并给出触发条件表 | 若检索索引不自动生成/更新，会出现“检索结果不可信” | 推荐 `novel-indexing-and-searching` 作为扩展技能，并强调“先检索再打开文件” | 作为扩展项而非核心能力时，长篇后期检索会成为瓶颈 |
| 工作流闭环 | 有“单章节写作 / 中断恢复 / 一致性问题处理 / 审阅问题处理”等流程化设计 | 流程更偏“研发团队 SOP”，个人写作者可能嫌繁琐而跳过 | 给出“开坑→写一章最小闭环→大修→设定变更”的清晰路径，并定义 DoD | DoD 依赖执行纪律；若没有自动门禁，很容易被“赶更新”打破 |
| 质量保障 | v1.1 提供**评估体系**（场景 + success criteria）与监控指标（触发率/错误率等） | 如果没有把评估绑定到日常流程，会变成“写在文档里的 QA” | 有连续性报告模板（P0/P1/P2）与冲突处理优先级（canon） | 评估粒度/覆盖面不如 A 系统化，难以量化“是不是在变好” |
| 设定变更（Retcon） | 有数据更新触发与协作流程，适合做影响面梳理与回修清单 | 如果数据源与正文脱节，会产生“以为修了，其实没修干净” | 给出 Retcon 安全工作流（decision-log→bible→continuity→editing→summaries→threads） | 影响分析缺少结构化索引支持时，回修范围容易漏章漏段 |
| 可扩展性/通用适配 | 有 `genre-settings.json` 等机制，适合把“类型参数”系统化 | JSON 配置多时容易走向“配置地狱”，特别是多类型/多视角混用 | 通过目录与模板扩展（assets/references/scripts），新增技能成本低 | 扩展多了之后，若没有统一 schema/索引，会出现“文件堆叠但不可检索” |
| 对起点连载友好度 | 更像“长期大型工程”，适合日更之外的系统化维护（卷末/大改/回收伏笔） | 日更高压下很可能简化流程，导致体系断裂 | 强调最小闭环与章末钩子可被模板化（scene cards/DoD），更贴合连载节奏 | 如果不补强自动化与评估，后期“爽点/钩子密度”与一致性会一起滑坡 |

---

## 2) 风险评估：各自最致命风险

| 方案 | 最致命风险（一句话） | 典型触发条件 | 直接后果 | 关键缓解（若继续用该方案） |
|---|---|---|---|---|
| A | **维护成本过高导致数据层失真**（作者不再更新/只更新正文），系统“看起来严谨、实际不可用” | 日更压力；数据文件太多；缺脚本自动更新；多人协作无约束 | 连续性检查/检索结果不可信；修设定变成“修一处漏三处”；写作速度被拖垮 | 把 JSON 维护变成**脚本生成**（从 Markdown/frontmatter 编译）；把更新触发绑定到 DoD；减少手填字段 |
| B | **缺少结构化索引导致“摘要漂移+检索退化”**，错误在长周期被放大 | 章节数上去后只靠 state/摘要；专名/ID 不统一；没有索引/搜索接口 | 回读找不到关键段；线索表/时间线漏更；设定冲突越来越隐蔽 | 引入核心 indexing（自动生成实体/章节/线索索引）；为关键实体强制最小 frontmatter；引入可量化评估与门禁 |

---

## 3) 方案 C：融合创新（保留优势，规避关键劣势）

### 3.1 C 的关键取舍（用一句话概括）

**写作者编辑 Markdown（设定/连续性/决策/大纲）作为权威记录；系统用脚本把其中可结构化的部分“编译”为可检索/可校验的索引；总控 Skill 用协议把写作闭环与质量门禁绑在一起。**

#### 3.1.1 权威优先级（防止多真相源漂移）

- **权威事实（canon）**：`novel/bible/**`、`novel/continuity/**`
- **变更裁决（why）**：`novel/decisions/decision-log.md`
- **计划与意图（plan）**：`novel/outline/**`
- **派生缓存（可重建）**：`novel/summaries/**`、`novel/_data/**`
- **叙事正文**：`novel/draft/**`

冲突优先级建议：`bible > continuity > decisions > outline > summaries > draft`

这同时保留：
- A 的：数据驱动、检索接口、评估体系、职责矩阵、上下文预算思想
- B 的：`novel/` 工作区、DoD 最小闭环、总控协议、写作友好模板

并规避：
- A 的“手填 JSON 地狱”
- B 的“后期检索与一致性失控”

### 3.2 统一工作区（单一真相源 + 生成索引）

建议以 B 的 `novel/` 为作品工作区，但增加“生成层”目录，明确**禁止手改**：

```
novel/
  config/
    novel.yaml                 # 体裁/视角/时态/禁忌/字数目标/卷章结构
  bible/                       # 权威设定（canon：世界观/角色/规则）
    characters/ char-*.md
    locations/  loc-*.md
    factions/   fac-*.md
    systems/    sys-*.md
    glossary.md
    style-guide.md
  outline/
    master-outline.md
    arcs/ arc-*.md
    scene-cards/ scn-*.md
  draft/
    chapters/ ch-001.md
  summaries/
    state.md
    chapters/ ch-001-summary.md
    volumes/  vol-01-summary.md
  continuity/                  # 权威连续性（canon：时间线/线索/硬约束）
    timeline.md
    open-threads.md
    constraints.md
    issues.md
  decisions/
    decision-log.md
  reports/
    continuity/ report-YYYYMMDD.md
    editing/    edit-pass-*.md
  _data/                        # 生成层（脚本输出，勿手改）
    entities.json
    chapter_index.json
    threads.json
    timeline.json
```

### 3.3 Skill 组成（1 总控 + 8 核心，职责更像 A、调度更像 B）

| Skill | 核心职责（做什么） | 明确边界（不做什么） | 主要读/写的文件（示例） |
|---|---|---|---|
| `novel-orchestrating`（总控） | 意图识别→路由→上下文选择→推进 DoD→触发评估/脚本 | 不直接产出长正文（只做调度/约束/检查） | 读 `state.md`；写“待办/门禁结果”（可写入 report） |
| `novel-project` | 初始化目录/模板；配置体裁参数；定义 DoD 与版本策略 | 不定义具体世界观/人物细节 | 写 `novel/config/novel.yaml`、初始化各模板 |
| `novel-worldbuilding` | 规则/地理/势力/体系的创建与维护（bible） | 不负责章节内表现与一致性检查 | 写 `novel/bible/systems/*`、`novel/bible/locations/*` |
| `novel-character-managing` | 人物卡/关系网/状态字段维护（bible） | 不负责“本章对白润色” | 写 `novel/bible/characters/*`、`relationships`（可在人物卡内） |
| `novel-plot-architecting` | 总大纲/卷纲/人物弧；把章节拆成 scene-cards | 不负责最终文笔输出 | 写 `novel/outline/*`、`scene-cards/*` |
| `novel-prose-crafting` | 基于 scene-card + state 写章；保证节奏/爽点/钩子 | 不负责更新 bible/索引（由闭环技能做） | 写 `novel/draft/chapters/*` |
| `novel-continuity-tracking` | 时间线/硬约束/线索承诺；输出连续性报告（P0/P1/P2） | 不改正文（只给清单/建议） | 写 `novel/continuity/*`、`novel/reports/continuity/*` |
| `novel-content-indexing` | 从 Markdown 编译索引；辅助生成/校验 summaries（`after_chapter` 门禁）；提供 search API/脚本；支持精准回读 | 不决定剧情/不写设定 | 写 `novel/summaries/**`（骨架/校验）与 `novel/_data/**`（生成） |
| `novel-manuscript-reviewing` | 润色/结构建议/改稿策略；与 continuity 联动做回修闭环 | 不改 bible（改设定走 decision→bible） | 写 `novel/reports/editing/*`，产出回修清单 |

### 3.4 上下文策略（A 的预算思想 + B 的读取顺序）

**默认读取顺序（永远先小后大）**：
1. `novel/summaries/state.md`
2. 本章 `scene-card` + 涉及实体的 `bible/*`
3. 上一章/相关章摘要（`summaries/chapters/*`）
4. 仅在发现冲突或要复用原句时，才“精准回读”正文（`draft/chapters/*`）

**预算表达改为“比例制”**（适配不同模型上下文窗口）：
- 写作会话：state+相关设定+场景卡 ≤ 30%｜最近摘要 ≤ 20%｜检索/原文引用 ≤ 20%｜留给生成与推理 ≥ 30%
- 审阅会话：允许把“检索/原文引用”提高到 40%，但强制输出 P0 清单（避免只读不改）

### 3.5 评估体系（把 A 的评估落到 B 的日常闭环里）

把评估拆两层：
- **章节级门禁（每章 DoD 必跑）**：是否更新 summary/state/threads；是否新增冲突写入 issues；是否维护章末钩子字段（连载必需）
- **里程碑评估（每 3~5 章/每卷）**：角色声线区分、时间线无自相矛盾、伏笔回收链路可追溯、爽点节拍是否按类型目标达标

评估产物建议写入：`novel/reports/continuity/report-*.md` 与 `novel/reports/editing/edit-pass-*.md`，并在 `state.md` 里更新“当前风险摘要”。

---

## 4) 方案 C 的具体执行步骤（落地路线图）

1. **确定“唯一真相源”**：规定权威事实只写 `novel/bible/**` 与 `novel/continuity/**`；正文仅叙事，不承担设定存储职责。  
2. **建立 `novel/` 目录骨架**：按 3.2 创建目录与空模板文件（scene-card/summary/state/decision-log/open-threads/timeline/issues）。  
3. **统一 ID 与最小 frontmatter**：人物/地点/线索/事件等统一 `char-*/loc-*/thr-*`；关键实体文件强制包含 `id/name/aliases/tags`（其余字段可选）。  
4. **写一个“总控协议”并固化在 `novel-orchestrating`**：把“读取顺序、冲突优先级、澄清策略、DoD 门禁、路由规则”写进总控 SKILL.md（正文保持短，细节放 references/）。  
5. **按职责矩阵创建 8 个核心 Skill 的最短路径工作流**：每个 SKILL.md 只写 3 件事：何时触发、最短步骤、读/写哪些文件；模板/清单放 assets/。  
6. **把 A 的“检索接口”变成可执行脚本**：在 `novel-content-indexing` 下提供 `build_index`/`search_chapters`/`search_entities`；输出写入 `novel/_data/*.json`（禁止手改）。  
7. **把“每章更新”变成半自动**：提供 `after_chapter` 门禁脚本（由 `novel-orchestrating` 触发）：只做摘要骨架生成 + 完整性检查（state/threads/timeline/issues 是否缺失），不猜设定、不自动改 canon。  
8. **把“连续性检查”变成可重复的报告**：`novel-continuity-tracking` 固定输出 P0/P1/P2；P0 必须可直接转成回修清单（章节号 + 搜索关键词 + 建议修法）。  
9. **把“起点连载要素”模板化**：scene-card 增加字段：本章爽点/章末钩子/引用的 `thr-*`（承诺）/回收的 `thr-*`；`open-threads.md` 作为线索状态权威源；DoD 增加“钩子落地 + 线索对账”。  
10. **先写 3~5 章做“真实压测”**：只允许用最小链路（scene→draft→summary/state→threads→index）；记录哪里最费时间，反向精简字段与流程。  
11. **补齐里程碑评估**：每 3~5 章跑一次“角色声线/伏笔链路/时间线一致性/爽点节拍”评估，把问题沉淀为 checklist 或脚本规则。  
12. **迭代触发词与边界**：根据误触发/漏触发调整 description；任何“技能互踩”都用职责矩阵修正，而不是在 SKILL.md 里加长篇解释。  

> 验收标准（你可以用它判断 C 是否真的跑起来）：  
> - 写到 30 章后仍能在 2 分钟内定位“某线索第一次出现在哪章哪段”。  
> - 每章都能在 DoD 门禁下完成 state/threads 更新，不靠记忆硬扛。  
> - 设定变更时能生成明确回修清单，并在 1~2 轮内收敛 P0。  
