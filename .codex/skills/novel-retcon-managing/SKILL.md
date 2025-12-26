---
name: novel-retcon-managing
description: 设定变更/吃书回修管理（Retcon）：评估改动影响范围，登记 decision log，生成回修清单，推进 bible→正文→摘要→线索→连续性复检的闭环。用于“改设定、推翻重做、发现前后矛盾需要统一口径、回收伏笔逻辑不成立需要重构”等高风险改动。
---

# 设定变更与回修（novel-retcon-managing）

## 目标

- 让“改一处崩全书”的风险可控：改动有记录、影响可定位、回修可对账。

## 权威与输入（按需）

- `novel/decisions/decision-log.md`（必须写）
- 受影响的 `novel/bible/**` 与 `novel/continuity/**`
- 受影响的章节（优先摘要，必要时回读正文）

## 最短路径工作流（安全 Retcon）

1. 先登记决策：在 `decision-log.md` 写清楚“为何改/替代方案/影响范围/回修清单/状态”。
2. 影响面定位：
   - 优先用实体 ID（`char-####`/`loc-####`/`sys-####`/`thr-####`；对应文件名通常为 `char-####-姓名.md` 等）与专名检索定位章节
   - 先列章节范围，再决定是否回读原文
3. 更新 canon：
   - 用 `novel-bible-managing` 更新 bible（权威事实）
   - 必要时更新 continuity（timeline/constraints/open threads）
4. 回修正文：
   - 用 `novel-editing` 按清单逐章修（避免漏改）
5. 更新派生缓存：
   - 用 `novel-summarizing` 更新受影响章节摘要 + state
   - 用 `novel-thread-tracking` 对账线索状态与回收窗口
6. 复检：
   - 跑 `novel-continuity-checking` 输出 P0 清单并收敛到 0
7. 收尾：把 `decision-log.md` 的状态推进到 done，并保留可追溯记录。

## 模板

如缺少 `decision-log.md`，复制 `assets/decision-log-template.md` 到 `novel/decisions/decision-log.md`。
