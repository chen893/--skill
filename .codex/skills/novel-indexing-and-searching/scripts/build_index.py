#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
从 novel/ 工作区构建可重建索引，写入 novel/_data/*.json。
仅使用标准库，不依赖第三方包。

索引设计目标：
- 足够有用（能快速定位实体/线索/章节）
- 足够稳（不要求完美 YAML 解析；只解析我们约定的最小 frontmatter 与表格）
"""

from __future__ import annotations

import argparse
import ast
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any


FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)


def parse_min_frontmatter(markdown_text: str) -> dict[str, Any]:
    """
    解析最小 frontmatter（仅支持 key: value 一行式）。
    支持 value 为：
    - "字符串" / '字符串'
    - [] / ["a","b"] 这类 Python 字面量风格列表
    """

    m = FRONTMATTER_RE.match(markdown_text)
    if not m:
        return {}
    raw = m.group(1)
    result: dict[str, Any] = {}
    for line in raw.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip()
        if not key:
            continue
        if value in ("", "null", "NULL", "~"):
            result[key] = None
            continue
        if value.startswith(("'", '"')) and value.endswith(("'", '"')) and len(value) >= 2:
            result[key] = value[1:-1]
            continue
        if value.startswith("[") and value.endswith("]"):
            try:
                result[key] = ast.literal_eval(value)
            except Exception:
                result[key] = value
            continue
        result[key] = value
    return result


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def parse_markdown_table(md: str, header_key: str) -> list[dict[str, str]]:
    """
    解析包含 header_key 的 Markdown 表格（| a | b |）。
    返回 rows：每行是 {col: value} 的 dict（字符串）。
    """

    lines = [ln.rstrip("\n") for ln in md.splitlines()]
    for i in range(len(lines) - 1):
        if header_key not in lines[i]:
            continue
        if "|" not in lines[i]:
            continue
        # 下一行应是分隔行 |---|
        if i + 1 >= len(lines) or "---" not in lines[i + 1]:
            continue
        header = [c.strip() for c in lines[i].strip().strip("|").split("|")]
        sep = lines[i + 1]
        if "|" not in sep:
            continue

        rows: list[dict[str, str]] = []
        for j in range(i + 2, len(lines)):
            row_line = lines[j].strip()
            if not row_line.startswith("|"):
                break
            cols = [c.strip() for c in row_line.strip().strip("|").split("|")]
            if len(cols) < len(header):
                cols += [""] * (len(header) - len(cols))
            row = {header[k]: cols[k] for k in range(len(header))}
            rows.append(row)
        return rows
    return []


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def chapter_sort_key(path: Path) -> tuple[int, str]:
    m = re.search(r"ch-(\d+)", path.stem)
    if not m:
        return (10**9, path.name)
    return (int(m.group(1)), path.name)


def count_chars_no_ws(text: str) -> int:
    return len(re.sub(r"\s+", "", text))


@dataclass
class Entity:
    entity_id: str
    name: str
    entity_type: str
    path: str
    aliases: list[str]
    tags: list[str]


def build_entities_index(novel_dir: Path) -> list[dict[str, Any]]:
    entities: list[Entity] = []

    type_map = {
        "characters": "character",
        "locations": "location",
        "factions": "faction",
        "items": "item",
        "systems": "system",
    }
    bible_dir = novel_dir / "bible"
    for folder, entity_type in type_map.items():
        root = bible_dir / folder
        if not root.exists():
            continue
        for path in sorted(root.glob("*.md")):
            text = read_text(path)
            fm = parse_min_frontmatter(text)
            entity_id = str(fm.get("id") or "").strip()
            name = str(fm.get("name") or "").strip()
            if not entity_id and not name:
                continue
            aliases = fm.get("aliases") if isinstance(fm.get("aliases"), list) else []
            tags = fm.get("tags") if isinstance(fm.get("tags"), list) else []
            entities.append(
                Entity(
                    entity_id=entity_id or path.stem,
                    name=name or path.stem,
                    entity_type=entity_type,
                    path=str(path.relative_to(novel_dir)).replace("\\", "/"),
                    aliases=[str(a) for a in aliases],
                    tags=[str(t) for t in tags],
                )
            )

    return [e.__dict__ for e in entities]


def build_chapter_index(novel_dir: Path) -> list[dict[str, Any]]:
    chapters_dir = novel_dir / "draft" / "chapters"
    out: list[dict[str, Any]] = []
    if not chapters_dir.exists():
        return out
    for path in sorted(chapters_dir.glob("ch-*.md"), key=chapter_sort_key):
        text = read_text(path)
        out.append(
            {
                "file": str(path.relative_to(novel_dir)).replace("\\", "/"),
                "title": next((ln.lstrip("# ").strip() for ln in text.splitlines() if ln.startswith("# ")), ""),
                "char_count": count_chars_no_ws(text),
                "line_count": len(text.splitlines()),
            }
        )
    return out


def build_threads_index(novel_dir: Path) -> list[dict[str, Any]]:
    path = novel_dir / "continuity" / "open-threads.md"
    if not path.exists():
        return []
    rows = parse_markdown_table(read_text(path), header_key="thread_id")
    return rows


def build_timeline_index(novel_dir: Path) -> list[dict[str, Any]]:
    path = novel_dir / "continuity" / "timeline.md"
    if not path.exists():
        return []
    rows = parse_markdown_table(read_text(path), header_key="event_id")
    return rows


def main() -> int:
    parser = argparse.ArgumentParser(description="构建 novel/_data 索引（entities/chapters/threads/timeline）")
    parser.add_argument("--root", default=".", help="项目根目录（默认：当前目录）")
    parser.add_argument("--novel-dir", default="novel", help="小说工作区目录名（默认：novel）")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    novel_dir = root / args.novel_dir
    if not novel_dir.exists():
        raise FileNotFoundError(f"找不到小说工作区：{novel_dir}")

    data_dir = novel_dir / "_data"
    data_dir.mkdir(parents=True, exist_ok=True)

    entities = build_entities_index(novel_dir)
    chapters = build_chapter_index(novel_dir)
    threads = build_threads_index(novel_dir)
    timeline = build_timeline_index(novel_dir)

    write_json(data_dir / "entities.json", {"entities": entities})
    write_json(data_dir / "chapter_index.json", {"chapters": chapters})
    write_json(data_dir / "threads.json", {"threads": threads})
    write_json(data_dir / "timeline.json", {"events": timeline})

    print("[OK] 索引已生成：")
    print(f"- {data_dir / 'entities.json'}")
    print(f"- {data_dir / 'chapter_index.json'}")
    print(f"- {data_dir / 'threads.json'}")
    print(f"- {data_dir / 'timeline.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

