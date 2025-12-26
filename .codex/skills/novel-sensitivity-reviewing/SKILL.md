---
name: novel-sensitivity-reviewing
description: 敏感点与平台风险自检：对章节内容做“风险提示与替代写法建议”，并输出可执行修改清单。用于“发布前自检、担心平台审核、需要降低敏感表达但不牺牲剧情效果”等需求。
---

# 敏感自检（novel-sensitivity-reviewing）

## 目标

- 只做风险提示与替代表达建议：帮助你降低平台风险，不做价值判断。

## 输入（按需）

- 目标章节：`novel/draft/chapters/ch-*.md`
- 风格指南/禁忌：`novel/config/novel.yaml`、`novel/bible/style-guide.md`

## 最短路径工作流

1. 明确检查范围与平台（不同平台尺度不同）。
2. 标注“高风险表达”的位置（引用章节与段落要点，不要大段复述）。
3. 给出替代写法：保持剧情功能（冲突/情绪/悬念）不变，替换表述方式。
4. 输出可执行清单：按 P0/P1 分级（P0=建议必改）。

## 参考清单

参阅 `references/sensitivity-checklist.md`。

