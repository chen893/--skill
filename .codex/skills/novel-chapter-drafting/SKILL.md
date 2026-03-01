---
name: novel-chapter-drafting
description: 根据场景卡与当前状态写章节正文：在不回读整书的前提下，优先读取 state+bible+scene-card+相关摘要，产出可连载的章节草稿并落到 draft/chapters/。用于“写/续写/扩写一章、日更、把场景卡写成正文、补充某段剧情并保持一致性与章末钩子”等需求。
---

# 章节写作（novel-chapter-drafting）

## 目标

- 用最小上下文写出“可发布的连载章节草稿”。
- 明确哪里是 canon、哪里是叙事：写正文不等于改设定。

## 输入（优先读取顺序）

1. `summaries/state.md`
2. 本卷规划/节拍（若有）：
   - `outline/volumes/vol-XX.md`
   - `outline/volumes/vol-XX-beat-sheet.md`
3. 本章 `outline/scene-cards/scn-*.md`
4. 相关 `bible/**`（人物/地点/体系/名词）
5. **风格对齐**：`bible/style-guide.md`（必读"AI 味黑名单"与"Show Don't Tell"章节）+ `bible/style-samples/*`（若有，读取样本对齐语感）
6. 上一章与相关章摘要 `summaries/chapters/*`
7. 仅在必要时精准回读 `draft/chapters/*`（引用原句/核对冲突）

## 输出（必须落盘）

- `draft/chapters/ch-XXX.md`

## 硬约束（必须遵守）

- 正文纯净：`draft/chapters/ch-XXX.md` 只写故事正文，不出现任何索引/元信息标记：
  - 不出现 `char-`/`loc-`/`fac-`/`item-`/`sys-`/`thr-`/`evt-`/`scn-` 等 ID 字符串
  - 不出现”系统面板/提示”类括号文本（如 `【提示：...】`、`【资源点线索已获得】`），除非用户明确要求写系统流/面板风
- 章节长度门槛：从 `config/novel.yaml` 读取 `chapter_length_min`/`chapter_length_max`（或从 `chapter_length_target` 解析区间），正文粗略字数（不含空白）不得低于下限；不达标就继续扩写”冲突代价、动作链、对话博弈、心理活动、细节信息增量”，禁止灌水。
- **去 AI 味（Show Don't Tell）——最高优先级**：
  - 严格遵守 `bible/style-guide.md` 中的”AI 味黑名单”：正文不出现黑名单中列举的任何句式/词组
  - 传递情绪禁止直接命名（愤怒/震惊/悲伤等），必须通过动作、生理反应、环境映射、物件交互来展示
  - 心理活动不超过正文 20%，且必须与当前动作/场景交织
  - 每个情绪高点必须有一个具体的、可视觉化的物理细节锚定
  - 比喻每千字最多 1 个，且必须贴合 POV 角色的认知范围（农民不会想到”量子纠缠”，剑修不会想到”化学反应”）
  - 禁止总结性旁白（”这一战让他明白了……”），让读者自己得出结论
  - 对白必须有区分度：写完后做”角色互换测试”——如果两个角色的台词互换仍然成立，说明同质化，必须改

## 最短路径工作流（写一章）

1. 确认本章目标：从场景卡提取 Goal/Conflict/Outcome/Beats。
2. 设定“章内节奏”：
   - 开场 10% 快速入戏（冲突/信息增量）
   - 中段升级代价（让推进有重量）
   - 末段落钩子（推动下一章的阅读动机）
3. 严守连续性约束：时间/地点/能力边界/已承诺线索（只在场景卡/摘要里用 thr-* 做作者标注，正文不写 ID）。
4. 写出正文（可先粗后细）：先把剧情推进写完整，再润色语气与细节。
5. 自检并补齐：
   - 字数不足：按”冲突代价→动作链→对话博弈→心理活动→环境细节→信息增量”顺序补写，直到达到下限
   - 文本污染：全文扫描并移除任何 ID 字符串与系统提示括号文本（把它们移到对应摘要/场景卡/线索表里）
   - **AI 味自检**：逐段扫描，对照 style-guide 的”AI 味黑名单”逐条检查；发现命中则改写为具体动作/感官/细节
   - 可选自动检查：如可运行命令，执行

     ```bash
     python .codex/skills/novel-chapter-drafting/scripts/qa_draft_chapter.py --root . --novel-dir . --chapter ch-XXX
     ```
     脚本会同时检测 ID 泄露和 AI 味高频句式，输出命中行与修改建议。
6. 若写作中出现“必须新增/改设定”才能成立：暂停正文输出，改为调用 `novel-bible-managing`（必要时登记 decision log），再回来续写。

## 写完后的闭环提醒（DoD）

写完本章后，通常需要继续调用：
- `novel-summarizing`：写章节摘要 + 更新 state
- `novel-thread-tracking`：对账 open threads（新增/回收）
- `novel-continuity-checking`：每 1~3 章做一次 P0/P1/P2 检查（可选但推荐）
