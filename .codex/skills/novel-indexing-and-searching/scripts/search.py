#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
在 novel/ 工作区内做简单检索（按文件范围过滤），输出命中行。
仅使用标准库。
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path


def iter_files(novel_dir: Path, scope: str) -> list[Path]:
    scopes = {
        "all": ["bible", "outline", "draft", "summaries", "continuity", "decisions", "reports"],
        "bible": ["bible"],
        "outline": ["outline"],
        "draft": ["draft"],
        "summaries": ["summaries"],
        "continuity": ["continuity"],
        "decisions": ["decisions"],
        "reports": ["reports"],
    }
    roots = scopes.get(scope, scopes["all"])
    files: list[Path] = []
    for r in roots:
        p = novel_dir / r
        if not p.exists():
            continue
        files.extend([x for x in p.rglob("*.md") if x.is_file()])
    return sorted(files)


def main() -> int:
    parser = argparse.ArgumentParser(description="在 novel/ 工作区检索关键词并输出命中行")
    parser.add_argument("--root", default=".", help="项目根目录（默认：当前目录）")
    parser.add_argument("--novel-dir", default="novel", help="小说工作区目录名（默认：novel）")
    parser.add_argument("--query", required=True, help="检索关键词（建议优先用 ID：char-/thr-/evt-）")
    parser.add_argument(
        "--scope",
        default="all",
        choices=["all", "bible", "outline", "draft", "summaries", "continuity", "decisions", "reports"],
        help="检索范围（默认：all）",
    )
    parser.add_argument("--regex", action="store_true", help="把 query 当作正则表达式")
    parser.add_argument("--max-results", type=int, default=50, help="最多输出多少条命中（默认：50）")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    novel_dir = root / args.novel_dir
    if not novel_dir.exists():
        raise FileNotFoundError(f"找不到小说工作区：{novel_dir}")

    files = iter_files(novel_dir, args.scope)
    if args.regex:
        pattern = re.compile(args.query)
        match_fn = lambda s: bool(pattern.search(s))
    else:
        match_fn = lambda s: args.query in s

    hits = 0
    for path in files:
        try:
            lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
        except Exception:
            continue
        for idx, line in enumerate(lines, start=1):
            if match_fn(line):
                rel = str(path.relative_to(root)).replace("\\", "/")
                print(f"{rel}:{idx}: {line}")
                hits += 1
                if hits >= args.max_results:
                    print(f"[STOP] 已达到最大输出条数：{args.max_results}")
                    return 0

    print(f"[OK] 检索完成：命中 {hits} 条（scope={args.scope}）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

