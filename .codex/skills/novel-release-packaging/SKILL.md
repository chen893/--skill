---
name: novel-release-packaging
description: 发布前打包与排版：检查章节命名/分章结构/标点与格式统一、敏感点自检、发布摘要与卷章导语、生成可复制粘贴的发布版本。用于“准备发布/上传、需要把草稿整理成平台可用文本、或发布前做一次快速质检与格式清理”等需求。
---

# 发布打包（novel-release-packaging）

## 目标

- 把“能写”变成“能发”：格式稳定、标点统一、敏感自检、章节可直接发布。

## 输入（按需）

- 目标章节/范围：`draft/chapters/ch-*.md`
- 风格约束：`bible/style-guide.md`
- 名词统一：`bible/glossary.md`
- 连续性问题清单：`continuity/issues.md`（若有）
- 若发布范围涉及“整卷”或卷间衔接（可选）：
  - `outline/volumes/vol-XX.md`
  - `summaries/volumes/vol-XX-summary.md`

## 输出（建议落盘）

- 发布检查清单（可直接复制执行）：`reports/release/release-YYYYMMDD.md`
- 卷首导语/上卷回顾（可选）：`reports/release/vol-XX-preface.md`
- 如需“发布版目录”（可选）：`release/`（按你的流程决定）

## 最短路径工作流（发布前 15 分钟）

1. 选定发布范围（例如：ch-081~ch-085）。
2. 若要提升卷间续读（可选）：生成“上卷回顾/本卷导语”（参考模板），避免读者断更后断片。
3. 做格式清理：
   - 标点是否遵循 `style-guide.md`
   - 引号/省略号/破折号是否统一
   - 小标题/分隔线是否干扰平台排版
4. 做名词统一：
   - 重点检查：人名/地名/组织名/境界名（对照 `glossary.md`）
5. 做敏感自检（只做“风险提示与替代措辞建议”，不做价值判断）。
6. 生成发布清单（见模板），把未解决项明确列出。

## 模板

复制 `assets/release-checklist-template.md` 作为起点。
如需卷首导语/上卷回顾，复制 `assets/volume-preface-template.md`。
