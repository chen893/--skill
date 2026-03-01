#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
章节草稿 QA：
- 检查是否达到章节字数门槛（粗略字符数：去除空白后的长度）
- 检查正文是否泄露索引/元信息（char-/loc-/thr- 等）或“系统提示括号文本”

仅使用标准库，不依赖第三方包。
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Any


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def normalize_text_for_count(text: str) -> str:
    return re.sub(r"\s+", "", text)


def chapter_sort_key(path: Path) -> tuple[int, str]:
    m = re.search(r"ch-(\d+)", path.stem)
    if not m:
        return (10**9, path.name)
    return (int(m.group(1)), path.name)


def parse_simple_yaml_kv(text: str) -> dict[str, str]:
    """
    极简 YAML 解析（仅支持顶层 key: value，忽略注释/列表/嵌套）。
    """

    out: dict[str, str] = {}
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("- "):
            continue
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip()
        if not key:
            continue
        if value.startswith(("'", '"')) and value.endswith(("'", '"')) and len(value) >= 2:
            value = value[1:-1]
        out[key] = value
    return out


def extract_ints(value: str) -> list[int]:
    return [int(x) for x in re.findall(r"\d+", value or "")]


def parse_chapter_length_constraints(config: dict[str, str]) -> tuple[int | None, int | None, int | None]:
    """
    返回 (min, max, target)。
    优先读取 chapter_length_min/max/target；否则从 chapter_length_target 里提取数字区间。
    """

    min_v = None
    max_v = None
    target_v = None

    if "chapter_length_min" in config:
        nums = extract_ints(config.get("chapter_length_min", ""))
        if nums:
            min_v = nums[0]
    if "chapter_length_max" in config:
        nums = extract_ints(config.get("chapter_length_max", ""))
        if nums:
            max_v = nums[0]
    if "chapter_length_target" in config:
        nums = extract_ints(config.get("chapter_length_target", ""))
        if len(nums) == 1:
            target_v = nums[0]
        elif len(nums) >= 2 and (min_v is None or max_v is None):
            # 兼容 "3000~5000" 这类写法
            min_v = min_v or nums[0]
            max_v = max_v or nums[1]

    return (min_v, max_v, target_v)


def resolve_chapter_path(novel_dir: Path, chapter: str | None) -> Path | None:
    chapters_dir = novel_dir / "draft" / "chapters"
    if chapter:
        p = Path(chapter)
        if p.is_absolute():
            return p

        # chapter 可能是相对路径（如 draft/chapters/ch-001.md）
        if p.parent != Path("."):
            return (novel_dir / p).resolve()

        name = chapter
        if not name.endswith(".md"):
            name = f"{name}.md"
        return (chapters_dir / name).resolve()

    if not chapters_dir.exists():
        return None
    files = sorted(chapters_dir.glob("ch-*.md"), key=chapter_sort_key)
    return files[-1].resolve() if files else None


FORBIDDEN_ID_RE = re.compile(r"\b(?:char|loc|fac|item|sys|thr|evt|scn)-")
FORBIDDEN_PANEL_RE = re.compile(r"(【提示：|【资源点|【关联线索：|【关联线索\\b)")


def find_hits(text: str) -> list[tuple[int, str, str]]:
    """
    返回 (line_no, kind, line)。
    """

    hits: list[tuple[int, str, str]] = []
    for idx, line in enumerate(text.splitlines(), start=1):
        if FORBIDDEN_ID_RE.search(line):
            hits.append((idx, "id_leak", line.rstrip()))
        if FORBIDDEN_PANEL_RE.search(line):
            hits.append((idx, "panel_text", line.rstrip()))
    return hits


def main() -> int:
    parser = argparse.ArgumentParser(description="章节草稿 QA：字数门槛 + 索引/系统提示泄露检查")
    parser.add_argument("--root", default=".", help="项目根目录（默认：当前目录）")
    parser.add_argument("--novel-dir", default="novel", help="小说工作区目录名（默认：novel；如在工作区内运行可填 .）")
    parser.add_argument(
        "--chapter",
        default=None,
        help="要检查的章节文件（ch-001 / ch-001.md / draft/chapters/ch-001.md）；不填则检查最新 ch-*.md",
    )
    parser.add_argument("--default-min", type=int, default=3000, help="未读到配置时的默认最小字数（默认：3000）")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    novel_dir = (root / args.novel_dir).resolve()
    if not novel_dir.exists():
        print(f"[ERR] 找不到小说工作区：{novel_dir}")
        return 2

    chapter_path = resolve_chapter_path(novel_dir, args.chapter)
    if chapter_path is None or not chapter_path.exists():
        print("[ERR] 未找到章节文件（draft/chapters/ch-*.md）。")
        return 2

    config_path = novel_dir / "config" / "novel.yaml"
    cfg: dict[str, str] = {}
    if config_path.exists():
        cfg = parse_simple_yaml_kv(read_text(config_path))

    min_len, max_len, target_len = parse_chapter_length_constraints(cfg)
    if min_len is None:
        min_len = args.default_min

    text = read_text(chapter_path)
    char_count = len(normalize_text_for_count(text))
    hits = find_hits(text)

    print("[INFO] 文件：", chapter_path)
    if config_path.exists():
        print("[INFO] 配置：", config_path)
    else:
        print("[WARN] 未找到配置：", config_path)
    print(f"[INFO] 字数（粗略，不含空白）：{char_count}")
    print(f"[INFO] 门槛：min={min_len}" + (f", max={max_len}" if max_len is not None else "") + (f", target={target_len}" if target_len is not None else ""))

    ok = True
    if char_count < min_len:
        ok = False
        print(f"[FAIL] 字数不足：还差 {min_len - char_count}")
    if max_len is not None and char_count > max_len:
        ok = False
        print(f"[FAIL] 字数超上限：超出 {char_count - max_len}")

    if hits:
        ok = False
        print("[FAIL] 发现索引/系统提示泄露（请移到 summaries/continuity/outline，或改写成正文自然表达）：")
        for line_no, kind, line in hits[:50]:
            print(f"- L{line_no} {kind}: {line}")
        if len(hits) > 50:
            print(f"[STOP] 已截断输出：{len(hits)} 条命中，仅展示前 50 条")

    if ok:
        print("[OK] 通过：字数达标且未检测到索引/系统提示泄露。")
        return 0

    return 2


if __name__ == "__main__":
    raise SystemExit(main())

