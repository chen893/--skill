#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
初始化 long-form 小说工作区（默认目录名为 `novel`，也可改为小说名）。

设计目标：
- 标准化目录结构与关键文件落盘位置
- 不引入第三方依赖（仅标准库）
- 默认只创建缺失项；--force 才覆盖已有模板文件
"""

from __future__ import annotations

import argparse
import re
import shutil
import sys
from pathlib import Path


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def write_template(template_path: Path, target_path: Path, force: bool) -> bool:
    if target_path.exists() and not force:
        return False
    ensure_dir(target_path.parent)
    shutil.copyfile(template_path, target_path)
    return True


WINDOWS_RESERVED_NAMES = {
    "CON",
    "PRN",
    "AUX",
    "NUL",
    *(f"COM{i}" for i in range(1, 10)),
    *(f"LPT{i}" for i in range(1, 10)),
}


def sanitize_dir_name(name: str) -> str:
    s = name.strip()
    if s.startswith("《") and s.endswith("》") and len(s) >= 3:
        s = s[1:-1].strip()
    s = s.strip().strip('"').strip("'").strip()
    s = re.sub(r'[<>:"/\\\\|?*]', "_", s)
    s = re.sub(r"\s+", " ", s).strip()
    s = s.rstrip(". ").strip()
    if not s:
        return "novel"
    if s.upper() in WINDOWS_RESERVED_NAMES:
        return f"{s}_"
    return s


def normalize_title(novel_name: str) -> str:
    s = novel_name.strip()
    if s.startswith(("'", '"')) and s.endswith(("'", '"')) and len(s) >= 2:
        s = s[1:-1].strip()
    if s.startswith("《") and s.endswith("》") and len(s) >= 3:
        return s
    return f"《{s}》"


def maybe_apply_novel_title(config_path: Path, novel_name: str) -> None:
    if not config_path.exists():
        return
    lines = config_path.read_text(encoding="utf-8", errors="ignore").splitlines(keepends=True)
    out: list[str] = []
    replaced = False
    for line in lines:
        if line.lstrip().startswith("title:"):
            out.append(f'title: "{normalize_title(novel_name)}"\n')
            replaced = True
        else:
            out.append(line)
    if not replaced:
        out.insert(0, f'title: "{normalize_title(novel_name)}"\n')
    config_path.write_text("".join(out), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="初始化小说工作区目录与基础模板文件")
    parser.add_argument("--root", default=".", help="项目根目录（默认：当前目录）")
    parser.add_argument("--novel-dir", default=None, help="工作区目录名（默认：novel；建议填小说名）")
    parser.add_argument("--novel-name", default=None, help="小说名（用于生成目录名并写入 config/novel.yaml 的 title）")
    parser.add_argument("--force", action="store_true", help="覆盖已存在的模板文件（谨慎使用）")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    novel_name = str(args.novel_name).strip() if args.novel_name else None

    novel_dir_name = args.novel_dir
    if novel_dir_name is None and novel_name:
        novel_dir_name = sanitize_dir_name(novel_name)

    if novel_dir_name is None and sys.stdin.isatty() and sys.stdout.isatty():
        user_input = input("小说工作区目录名（默认：novel；建议填小说名）：").strip()
        if user_input:
            novel_dir_name = sanitize_dir_name(user_input)
            novel_name = novel_name or user_input

    novel_dir_name = novel_dir_name or "novel"
    novel_dir = root / novel_dir_name

    dirs_to_create = [
        novel_dir / "config",
        novel_dir / "bible" / "characters",
        novel_dir / "bible" / "locations",
        novel_dir / "bible" / "factions",
        novel_dir / "bible" / "items",
        novel_dir / "bible" / "systems",
        novel_dir / "outline" / "arcs",
        novel_dir / "outline" / "scene-cards",
        novel_dir / "draft" / "chapters",
        novel_dir / "summaries" / "chapters",
        novel_dir / "summaries" / "volumes",
        novel_dir / "continuity",
        novel_dir / "decisions",
        novel_dir / "research" / "sources",
        novel_dir / "reports" / "continuity",
        novel_dir / "reports" / "editing",
        novel_dir / "_data",
    ]

    for d in dirs_to_create:
        ensure_dir(d)

    assets_dir = Path(__file__).resolve().parent.parent / "assets"
    template_to_target = {
        "AGENTS.md": novel_dir / "AGENTS.md",
        "novel.yaml": novel_dir / "config" / "novel.yaml",
        "style-guide.md": novel_dir / "bible" / "style-guide.md",
        "glossary.md": novel_dir / "bible" / "glossary.md",
        "state.md": novel_dir / "summaries" / "state.md",
        "open-threads.md": novel_dir / "continuity" / "open-threads.md",
        "timeline.md": novel_dir / "continuity" / "timeline.md",
        "issues.md": novel_dir / "continuity" / "issues.md",
        "constraints.md": novel_dir / "continuity" / "constraints.md",
        "decision-log.md": novel_dir / "decisions" / "decision-log.md",
    }

    missing_templates = [name for name in template_to_target.keys() if not (assets_dir / name).exists()]
    if missing_templates:
        raise FileNotFoundError(f"assets/ 缺少模板文件：{', '.join(missing_templates)}")

    wrote: dict[str, bool] = {}
    for template_name, target_path in template_to_target.items():
        wrote[template_name] = write_template(assets_dir / template_name, target_path, args.force)

    if novel_name and wrote.get("novel.yaml"):
        maybe_apply_novel_title(novel_dir / "config" / "novel.yaml", novel_name)

    print(f"[OK] 工作区已初始化：{novel_dir}")
    print("下一步建议：先写 bible（硬约束）→ 大纲 → 场景卡 → 写章闭环")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
