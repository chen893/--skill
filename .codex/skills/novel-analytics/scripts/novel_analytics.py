#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
统计 novel/draft/chapters 下的章节字数/章长分布，并输出中文 Markdown 报告。
仅使用标准库，不依赖第三方包。
"""

from __future__ import annotations

import argparse
import datetime as dt
import re
from pathlib import Path


def normalize_text_for_count(text: str) -> str:
    # 去掉所有空白（换行/空格/制表等），用于粗略字数（字符数）统计
    return re.sub(r"\s+", "", text)


def chapter_sort_key(path: Path) -> tuple[int, str]:
    m = re.search(r"ch-(\d+)", path.stem)
    if not m:
        return (10**9, path.name)
    return (int(m.group(1)), path.name)


def main() -> int:
    parser = argparse.ArgumentParser(description="统计小说章节字数/章长分布并输出报告")
    parser.add_argument("--root", default=".", help="项目根目录（默认：当前目录）")
    parser.add_argument("--novel-dir", default="novel", help="小说工作区目录名（默认：novel）")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    novel_dir = root / args.novel_dir
    chapters_dir = novel_dir / "draft" / "chapters"

    if not chapters_dir.exists():
        raise FileNotFoundError(f"找不到章节目录：{chapters_dir}")

    chapter_files = sorted(chapters_dir.glob("ch-*.md"), key=chapter_sort_key)
    if not chapter_files:
        print("未找到任何章节文件（ch-*.md）。")
        return 0

    rows = []
    total_chars = 0
    lengths = []
    for path in chapter_files:
        text = path.read_text(encoding="utf-8", errors="ignore")
        count = len(normalize_text_for_count(text))
        total_chars += count
        lengths.append(count)
        rows.append((path.name, count))

    avg = total_chars / max(1, len(rows))
    min_len = min(lengths)
    max_len = max(lengths)

    today = dt.date.today().isoformat()
    report_dir = novel_dir / "reports" / "analytics"
    report_dir.mkdir(parents=True, exist_ok=True)
    report_path = report_dir / f"report-{today}.md"

    lines = []
    lines.append(f"# 写作统计报告（{today}）\n")
    lines.append("## 总览\n")
    lines.append(f"- 章节数：{len(rows)}\n")
    lines.append(f"- 总字数（粗略字符数，不含空白）：{total_chars}\n")
    lines.append(f"- 平均章长：{avg:.0f}\n")
    lines.append(f"- 最短/最长：{min_len} / {max_len}\n")
    lines.append("\n")
    lines.append("## 章长明细\n")
    lines.append("| 章节文件 | 字数（粗略） |\n")
    lines.append("|---|---:|\n")
    for name, count in rows:
        lines.append(f"| {name} | {count} |\n")
    lines.append("\n")
    lines.append("## 信号与建议（只给可执行项）\n")
    lines.append("- 若章长波动过大：考虑固定“开场入戏/中段升级/末段钩子”的节奏比例。\n")
    lines.append("- 若章长长期偏短：优先补“冲突代价与信息增量”，不要用无意义描写灌水。\n")
    lines.append("- 若章长长期偏长：优先拆成 2 章的场景卡，避免读者疲劳。\n")

    report_path.write_text("".join(lines), encoding="utf-8")
    print(f"[OK] 已生成报告：{report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

