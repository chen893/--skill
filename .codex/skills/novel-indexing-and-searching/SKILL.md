---
name: novel-indexing-and-searching
description: 索引与检索：为长篇生成可重建的本地索引（entities/chapters/threads/timeline），并提供按 ID/专名/关键词快速定位“在哪章哪段”的检索工具。用于“找某段原文、查某角色/线索首次出现、定位冲突来源、避免回读整章整卷”等需求。
---

# 索引与检索（novel-indexing-and-searching）

## 目标

- 先检索、再打开文件：把“回读整书”变成“精准定位到行”。
- 索引是派生缓存：写到 `WORKDIR/_data/**`，可随时重建，禁止手改（WORKDIR 为工作区目录名，默认 `novel`）。

## 核心约定（让索引靠谱）

- 关键实体使用稳定 ID：`char-*`/`loc-*`/`fac-*`/`item-*`/`sys-*`/`thr-*`/`evt-*`
- `open-threads.md` 与 `timeline.md` 尽量保持表格结构（便于解析）

## 最短路径工作流

### 1) 生成/更新索引

在项目根目录执行：

```bash
python .codex/skills/novel-indexing-and-searching/scripts/build_index.py --root .
```

输出写入：
- `WORKDIR/_data/entities.json`
- `WORKDIR/_data/chapter_index.json`
- `WORKDIR/_data/threads.json`
- `WORKDIR/_data/timeline.json`

### 2) 执行检索

在项目根目录执行：

```bash
python .codex/skills/novel-indexing-and-searching/scripts/search.py --root . --query "thr-0007"
```

常用技巧：
- 优先搜 ID（最稳定），其次搜专名（次稳定），最后才搜泛关键词
- 先在 `summaries/` 与 `continuity/` 搜，再回到 `draft/` 精准回读正文
- 若工作区目录名不是 `novel`：两条命令都加 `--novel-dir WORKDIR`。
