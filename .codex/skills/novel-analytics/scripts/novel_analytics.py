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


def chapter_number(path: Path) -> int | None:
    m = re.search(r"ch-(\d+)", path.stem)
    return int(m.group(1)) if m else None


def parse_volume_range(novel_dir: Path, volume_id: str) -> tuple[int | None, int | None]:
    """
    从 outline/volumes/<vol-XX>.md 的 frontmatter 里读取 range: "ch-001~ch-080" 并解析为数字区间。
    失败则返回 (None, None)。
    """

    path = novel_dir / "outline" / "volumes" / f"{volume_id}.md"
    if not path.exists():
        return (None, None)
    text = path.read_text(encoding="utf-8", errors="ignore")
    # 只在 frontmatter 内找 range
    m = re.search(r"^---\s*\n(.*?)\n---\s*\n", text, flags=re.DOTALL)
    if not m:
        return (None, None)
    fm = m.group(1)
    m2 = re.search(r"^range:\s*(.+?)\s*$", fm, flags=re.MULTILINE)
    if not m2:
        return (None, None)
    raw = m2.group(1).strip().strip('"').strip("'").strip()
    nums = [int(x) for x in re.findall(r"ch-(\d+)", raw)]
    if len(nums) >= 2:
        return (nums[0], nums[1])
    if len(nums) == 1:
        return (nums[0], None)
    nums2 = [int(x) for x in re.findall(r"\d+", raw)]
    if len(nums2) >= 2:
        return (nums2[0], nums2[1])
    if len(nums2) == 1:
        return (nums2[0], None)
    return (None, None)


def main() -> int:
    parser = argparse.ArgumentParser(description="统计小说章节字数/章长分布并输出报告")
    parser.add_argument("--root", default=".", help="项目根目录（默认：当前目录）")
    parser.add_argument("--novel-dir", default="novel", help="小说工作区目录名（默认：novel）")
    parser.add_argument("--volume", default=None, help="按卷统计（例如：vol-01；从 outline/volumes/vol-01.md 读取 range）")
    parser.add_argument("--ch-from", type=int, default=None, help="只统计从 ch-XXX 开始的章节（数字部分，例如 1 表示 ch-001）")
    parser.add_argument("--ch-to", type=int, default=None, help="只统计到 ch-XXX 为止的章节（数字部分，例如 80 表示 ch-080）")
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

    if args.volume and (args.ch_from is not None or args.ch_to is not None):
        raise ValueError("请在 --volume 与 --ch-from/--ch-to 之间二选一（避免统计范围冲突）。")

    ch_from = args.ch_from
    ch_to = args.ch_to
    volume_id = None
    if args.volume:
        volume_id = str(args.volume).strip()
        vr_from, vr_to = parse_volume_range(novel_dir, volume_id)
        ch_from = vr_from
        ch_to = vr_to

    if ch_from is not None or ch_to is not None:
        filtered = []
        for p in chapter_files:
            n = chapter_number(p)
            if n is None:
                continue
            if ch_from is not None and n < ch_from:
                continue
            if ch_to is not None and n > ch_to:
                continue
            filtered.append(p)
        chapter_files = filtered

    if not chapter_files:
        print("在指定范围内未找到任何章节文件。")
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
    suffix = f"{volume_id}-" if volume_id else ""
    report_path = report_dir / f"{suffix}report-{today}.md"

    lines = []
    lines.append(f"# 写作统计报告（{today}）\n")
    lines.append("## 总览\n")
    if volume_id:
        lines.append(f"- 统计范围：{volume_id}\n")
    if ch_from is not None or ch_to is not None:
        if ch_from is not None and ch_to is not None:
            ch_range_text = f"ch-{ch_from:03d} ~ ch-{ch_to:03d}"
        elif ch_from is not None:
            ch_range_text = f"ch-{ch_from:03d} ~"
        else:
            ch_range_text = f"~ ch-{ch_to:03d}"
        lines.append(f"- 章节范围：{ch_range_text}\n")
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
