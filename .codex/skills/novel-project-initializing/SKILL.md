---
name: novel-project-initializing
description: 初始化/重建长篇小说工作区（默认直接使用小说名目录，不再生成 novel/ 子目录）：创建目录结构，生成基础模板（config、style-guide、state、open threads、timeline、issues、decision log 等）。用于开新书、把旧稿迁移进结构化目录、或工作区缺失/损坏需要补齐时。
---

# 小说项目初始化（novel-project-initializing）

## 目标

- 一键落地“以小说名为根目录”的工作区骨架，让后续写作/检索/一致性检查都有“可持续的落盘位置”。
- 用尽量少的模板文件，把“长篇必需的记忆系统”立起来（state / 线索 / 时间线 / 决策）。

## 输出位置（默认）

- 默认生成到 `--novel-name` 对应目录下：例如 `--root projects --novel-name "书名"` 会生成 `projects/书名/...`（不包含 `novel/` 这一层）
- 如果 `--root` 本身就是小说目录（例如 `--root projects/书名 --novel-name "书名"`），脚本会自动“就地初始化”为 `projects/书名/...`
- 也可显式指定 `--novel-dir`：填小说名或相对路径；填 `.` 表示直接在 `--root` 下初始化
- 同时复制 `.codex/skills` 到 `WORKDIR/.codex/skills`，让工作区可自包含迁移/离线使用
- 禁止手改生成层：`WORKDIR/_data/`（由索引/统计脚本生成；WORKDIR 为工作区目录名）

## 最短路径工作流

### 方式 A：运行初始化脚本（推荐）

在项目根目录执行：

```bash
python .codex/skills/novel-project-initializing/scripts/init_novel_workspace.py --root projects --novel-name "书名"
```

如果你不使用 `projects/` 作为总目录，把 `--root` 直接改成 `.` 即可（会生成 `./书名/...`）。

可选参数：

- `--novel-name`：小说名（会写入 `config/novel.yaml` 的 `title`；未显式指定 `--novel-dir` 时也会用于生成目录名）
- `--novel-dir`：工作区目录名或相对路径（不填时默认用 `--novel-name`；填 `.` 表示直接在 `--root` 下初始化）
- `--force`：覆盖已有模板文件，并重建 `WORKDIR/.codex/skills`（谨慎使用）

### 方式 B：手动创建（脚本不可用时）

1. 创建目录：`config/ bible/ outline/ draft/ summaries/ continuity/ decisions/ reports/ research/ _data/`
2. 创建基础文件（可从本 skill 的 `assets/` 复制）：
   - `WORKDIR/AGENTS.md`
   - `WORKDIR/config/novel.yaml`
   - `WORKDIR/bible/style-guide.md`
   - `WORKDIR/bible/glossary.md`
   - `WORKDIR/summaries/state.md`
   - `WORKDIR/continuity/open-threads.md`
   - `WORKDIR/continuity/timeline.md`
   - `WORKDIR/continuity/issues.md`
   - `WORKDIR/decisions/decision-log.md`

## 初始化后下一步（建议顺序）

1. 用 `novel-bible-managing` 先写“硬约束”（世界规则/时间线基准/人物核心动机）。
2. 用 `novel-outlining` 产出 `master-outline.md`（主线 + 终局 + 主题承诺）。
3. 用 `novel-scene-planning` 拆前 1~3 章场景卡。
4. 进入写章闭环：`novel-chapter-drafting` → `novel-summarizing` → `novel-thread-tracking`（每 1~3 章可跑 `novel-continuity-checking`）。

## 资源

### scripts/

运行 `scripts/init_novel_workspace.py` 生成工作区目录与基础文件（默认目录名为 `novel`）。

### assets/

基础模板（全部中文）：`novel.yaml`、`style-guide.md`、`glossary.md`、`state.md`、`open-threads.md`、`timeline.md`、`issues.md`、`decision-log.md`。

另外会生成：`WORKDIR/AGENTS.md`（提示 Codex 在工作区下如何路由调用各 `novel-*` skills）。
