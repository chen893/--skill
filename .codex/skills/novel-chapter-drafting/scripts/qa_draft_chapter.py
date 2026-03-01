#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
章节草稿 QA：
- 检查是否达到章节字数门槛（粗略字符数：去除空白后的长度）
- 检查正文是否泄露索引/元信息（char-/loc-/thr- 等）或"系统提示括号文本"
- 按密度检测 AI 味高频句式（区分叙述/对白，按聚集程度分级报警）

仅使用标准库，不依赖第三方包。
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path


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
            min_v = min_v or nums[0]
            max_v = max_v or nums[1]

    return (min_v, max_v, target_v)


def resolve_chapter_path(novel_dir: Path, chapter: str | None) -> Path | None:
    chapters_dir = novel_dir / "draft" / "chapters"
    if chapter:
        p = Path(chapter)
        if p.is_absolute():
            return p

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


# ---------------------------------------------------------------------------
# 硬性禁止（零容忍，单次命中即 FAIL）
# ---------------------------------------------------------------------------
FORBIDDEN_ID_RE = re.compile(r"\b(?:char|loc|fac|item|sys|thr|evt|scn)-")
FORBIDDEN_PANEL_RE = re.compile(r"(【提示：|【资源点|【关联线索：|【关联线索\\b)")


# ---------------------------------------------------------------------------
# AI 味检测：基于密度的柔性规则
#
# 设计原则：
#   - 单次出现不一定有问题，高频聚集才是 AI 味的本质
#   - 对白（引号内）和叙述（引号外）分开计数，对白更宽容
#   - 按"每千字命中数"分级：
#       density < warn_per_k  → 不报（正常写作也会偶尔用到）
#       warn_per_k <= density < fail_per_k → WARN（提醒注意）
#       density >= fail_per_k → FAIL（几乎可以确定是 AI 味聚集）
#   - dialogue_exempt=True 的规则：对白中命中不计入密度
# ---------------------------------------------------------------------------

class AiFlavorRule:
    __slots__ = ("pattern", "category", "suggestion", "warn_per_k", "fail_per_k", "dialogue_exempt")

    def __init__(
        self,
        pattern: str,
        category: str,
        suggestion: str,
        warn_per_k: float = 1.0,
        fail_per_k: float = 2.0,
        dialogue_exempt: bool = False,
    ):
        self.pattern = re.compile(pattern)
        self.category = category
        self.suggestion = suggestion
        self.warn_per_k = warn_per_k    # 每千字 >= 此值才 WARN
        self.fail_per_k = fail_per_k    # 每千字 >= 此值才 FAIL
        self.dialogue_exempt = dialogue_exempt  # True = 对白中出现不扣分


# ── 对白边界检测 ──
# 粗略判定：行内有中文引号包裹的内容视为对白
_DIALOGUE_RE = re.compile(r'[""「」]')


def is_inside_dialogue(line: str, match_start: int) -> bool:
    """粗略判断 match_start 位置是否在引号内。"""
    # 数 match_start 之前的引号开闭数
    before = line[:match_start]
    opens = before.count("\u201c") + before.count("\u300c")   # " 「
    closes = before.count("\u201d") + before.count("\u300d")  # " 」
    return opens > closes


AI_RULES: list[AiFlavorRule] = [
    # ── 情绪直接命名 ──
    # 叙述中高频使用是典型 AI 味，但偶尔一次没问题
    AiFlavorRule(
        r"心中涌起.{0,2}(愤怒|悲伤|暖意|暖流|复杂|说不清|难以名状|莫名)",
        "情绪命名", "试试动作/生理反应：'拳头攥紧''后槽牙咬得咯吱响'",
        warn_per_k=0.5, fail_per_k=1.5,
    ),
    AiFlavorRule(
        r"感到一阵.{0,2}(心寒|心悸|失落|不安|恐惧|眩晕|窒息)",
        "情绪命名", "试试身体反应：'胃里翻涌了一下''后背的汗毛竖了起来'",
        warn_per_k=0.5, fail_per_k=1.5,
    ),
    AiFlavorRule(
        r"眼中闪过一丝.{0,4}(精光|杀意|惊讶|笑意|冷意|狠厉|玩味)",
        "情绪命名", "试试眼部动作：'眼皮跳了一下''目光钉在对方颈侧'",
        warn_per_k=0.5, fail_per_k=1.5,
    ),
    AiFlavorRule(
        r"内心深处.{0,6}(涌起|翻涌|蠢蠢欲动|某种)",
        "情绪命名", "用外在行为暗示内心",
        warn_per_k=0.3, fail_per_k=1.0,
    ),
    AiFlavorRule(
        r"一股无名的.{0,6}涌上心头",
        "情绪命名", "太空泛，换成具体的生理感受",
        warn_per_k=0.3, fail_per_k=1.0,
    ),
    AiFlavorRule(
        r"心中五味杂陈",
        "情绪命名", "用一个具体的矛盾行为替代",
        warn_per_k=0.3, fail_per_k=1.0,
    ),
    AiFlavorRule(
        r"不由得心头一(紧|沉|颤|震|酸)",
        "情绪命名", "试试动作：'脚步顿了一拍''杯子没端稳'",
        warn_per_k=0.5, fail_per_k=1.5,
    ),

    # ── 万能过渡废句 ──
    AiFlavorRule(
        r"与此同时",
        "过渡废句", "直接切场景，或用动作衔接",
        warn_per_k=0.5, fail_per_k=1.0,
    ),
    AiFlavorRule(
        r"仿佛在回应.{0,4}(想法|心声|内心|念头)似的",
        "过渡废句", "删掉，直接写发生了什么",
        warn_per_k=0.3, fail_per_k=0.8,
    ),
    AiFlavorRule(
        r"这一刻.{0,4}(他|她|它).{0,4}(突然|忽然|终于)(明白|理解|懂得|意识到)",
        "过渡废句", "用行动表达领悟，不要旁白点破",
        warn_per_k=0.3, fail_per_k=1.0,
    ),
    AiFlavorRule(
        r"(?<![""「])不知为何(?![""」])",  # 对白里说"不知为何"很自然，只查叙述
        "过渡废句", "要么给原因，要么删掉",
        warn_per_k=0.5, fail_per_k=1.5, dialogue_exempt=True,
    ),
    AiFlavorRule(
        r"似乎感受到了什么",
        "过渡废句", "写清楚感受到了什么，或者不写",
        warn_per_k=0.3, fail_per_k=0.8,
    ),
    AiFlavorRule(
        r"仿佛下定了某种决心",
        "过渡废句", "用行动表现决心：站起来/转身/开口",
        warn_per_k=0.3, fail_per_k=0.8,
    ),
    AiFlavorRule(
        r"时间仿佛.{0,4}(静止|凝固|停滞|慢了下来)",
        "过渡废句", "用感官细节替代：如'秒针的声音突然变得很响'",
        warn_per_k=0.3, fail_per_k=1.0,
    ),
    AiFlavorRule(
        r"空气中弥漫着.{0,6}(气氛|氛围|味道|气息)",
        "过渡废句", "写具体的感官：温度/声音/气味",
        warn_per_k=0.3, fail_per_k=1.0,
    ),
    AiFlavorRule(
        r"气氛.{0,4}变得.{0,4}(微妙|尴尬|紧张|凝重)",
        "过渡废句", "用人物反应传递气氛：如'没人再动筷子'",
        warn_per_k=0.3, fail_per_k=1.0,
    ),

    # ── 总结性旁白 ──
    # 这类句式即使出现一次也很扎眼，阈值更低
    AiFlavorRule(
        r"这(场|次|一)(战斗|经历|遭遇|事件).{0,6}让.{1,4}(明白|懂得|学会|意识到)",
        "总结旁白", "删掉，读者会自己总结",
        warn_per_k=0.2, fail_per_k=0.5,
    ),
    AiFlavorRule(
        r"(他|她)知道.{0,4}从此以后.{0,8}(不同|改变|不再)",
        "总结旁白", "用后续行为展示变化",
        warn_per_k=0.2, fail_per_k=0.5,
    ),
    AiFlavorRule(
        r"(这一战|这一刻|这件事).{0,6}(注定|必将).{0,6}(载入|铭记|改写)",
        "总结旁白", "过度拔高，删掉",
        warn_per_k=0.2, fail_per_k=0.5,
    ),
    AiFlavorRule(
        r"也许.{0,4}这就是所谓的",
        "总结旁白", "删掉",
        warn_per_k=0.2, fail_per_k=0.5,
    ),
    AiFlavorRule(
        r"而这.{0,4}(仅仅|只)是.{0,6}(开始|序幕|序章)",
        "总结旁白", "章末钩子不需要旁白点破",
        warn_per_k=0.2, fail_per_k=0.5,
    ),
    AiFlavorRule(
        r"命运的齿轮.{0,6}(开始|已经).{0,4}(转动|旋转)",
        "总结旁白", "删掉",
        warn_per_k=0.2, fail_per_k=0.3,
    ),
    AiFlavorRule(
        r"故事.{0,4}(远|还|并)没有结束",
        "总结旁白", "删掉",
        warn_per_k=0.2, fail_per_k=0.3,
    ),

    # ── 修辞通胀 ──
    AiFlavorRule(
        r"(宛如|犹如|仿佛|好似|恰如).{0,6}(沉睡|苏醒)的(巨兽|猛兽|巨龙|凶兽)",
        "修辞通胀", "换一个贴合 POV 认知的具体比喻",
        warn_per_k=0.2, fail_per_k=0.5,
    ),
    AiFlavorRule(
        r"(犹如|宛如|仿佛|好似).{0,4}(锋利|锐利)的(刀|剑|利刃|刀刃)",
        "修辞通胀", "换一个更具体的感官比喻",
        warn_per_k=0.2, fail_per_k=0.5,
    ),
    AiFlavorRule(
        r"像是被一只无形的手",
        "修辞通胀", "用具体施力感替代：如'胸口像压了块石板'",
        warn_per_k=0.2, fail_per_k=0.5,
    ),

    # ── 情感递进公式 ──
    AiFlavorRule(
        r"先是.{1,6}(随后|然后|接着|紧接着)是?.{0,4}(不敢置信|难以相信|震惊).{0,6}(最后|最终|终于)",
        "递进公式", "打乱顺序，或只写最终状态的行为表现",
        warn_per_k=0.2, fail_per_k=0.5,
    ),
    AiFlavorRule(
        r"从最初的.{1,8}到后来的.{1,8}再到(现在|如今|此刻)的",
        "递进公式", "删掉时间轴总结，用一个细节暗示变化",
        warn_per_k=0.2, fail_per_k=0.5,
    ),
    AiFlavorRule(
        r"(他|她)的(表情|脸色|眼神|神情)从.{1,6}变成了?.{1,6}(最终|最后)?(定格|停留|落)在",
        "递进公式", "只写最终的表情+一个微动作",
        warn_per_k=0.3, fail_per_k=0.8,
    ),

    # ── 对白污染 ──
    # 对白规则只看引号内，且阈值更宽松（角色偶尔说一次"有意思"不是罪）
    AiFlavorRule(
        r"["\u201c「]看来.{0,8}果然如此["\u201d」]",
        "对白污染", "换成角色特有的反应方式",
        warn_per_k=0.3, fail_per_k=0.8,
    ),
]


# ---------------------------------------------------------------------------
# 命中结构
# ---------------------------------------------------------------------------

class Hit:
    __slots__ = ("line_no", "kind", "line", "suggestion", "in_dialogue")

    def __init__(self, line_no: int, kind: str, line: str, suggestion: str, in_dialogue: bool = False):
        self.line_no = line_no
        self.kind = kind
        self.line = line
        self.suggestion = suggestion
        self.in_dialogue = in_dialogue


def find_forbidden_hits(text: str) -> list[Hit]:
    """ID 泄露 / 系统面板 — 零容忍。"""
    hits: list[Hit] = []
    for idx, line in enumerate(text.splitlines(), start=1):
        if FORBIDDEN_ID_RE.search(line):
            hits.append(Hit(idx, "id_leak", line.rstrip(), "移到 summaries/continuity/outline"))
        if FORBIDDEN_PANEL_RE.search(line):
            hits.append(Hit(idx, "panel_text", line.rstrip(), "改写成正文自然表达"))
    return hits


def find_ai_flavor_hits(text: str) -> list[Hit]:
    """AI 味句式 — 记录所有命中，后续按密度分级。"""
    hits: list[Hit] = []
    for idx, line in enumerate(text.splitlines(), start=1):
        for rule in AI_RULES:
            m = rule.pattern.search(line)
            if not m:
                continue
            in_dlg = is_inside_dialogue(line, m.start())
            if rule.dialogue_exempt and in_dlg:
                continue
            hits.append(Hit(idx, f"ai/{rule.category}", line.rstrip(), rule.suggestion, in_dlg))
            break  # 每行只报第一条命中
    return hits


def compute_density_report(
    ai_hits: list[Hit], char_count: int
) -> tuple[dict[str, list[Hit]], dict[str, str]]:
    """
    按 category 聚合命中，计算每千字密度，与规则阈值比较返回级别。
    返回:
      by_cat: { category: [Hit, ...] }
      levels: { category: "ok" | "warn" | "fail" }
    """
    by_cat: dict[str, list[Hit]] = {}
    for h in ai_hits:
        cat = h.kind.split("/", 1)[1] if "/" in h.kind else h.kind
        by_cat.setdefault(cat, []).append(h)

    k = max(char_count / 1000.0, 0.5)  # 避免除零

    # 找每个 category 对应的阈值（取第一条匹配规则的设置）
    cat_thresholds: dict[str, tuple[float, float]] = {}
    for rule in AI_RULES:
        if rule.category not in cat_thresholds:
            cat_thresholds[rule.category] = (rule.warn_per_k, rule.fail_per_k)

    levels: dict[str, str] = {}
    for cat, hits_list in by_cat.items():
        # 排除对白中的命中来计算叙述密度
        narr_count = sum(1 for h in hits_list if not h.in_dialogue)
        density = narr_count / k
        warn_t, fail_t = cat_thresholds.get(cat, (1.0, 2.0))
        if density >= fail_t:
            levels[cat] = "fail"
        elif density >= warn_t:
            levels[cat] = "warn"
        else:
            levels[cat] = "ok"

    return by_cat, levels


def main() -> int:
    parser = argparse.ArgumentParser(description="章节草稿 QA：字数门槛 + 索引泄露 + AI 味密度检测")
    parser.add_argument("--root", default=".", help="项目根目录（默认：当前目录）")
    parser.add_argument("--novel-dir", default="novel", help="小说工作区目录名（默认：novel；如在工作区内运行可填 .）")
    parser.add_argument(
        "--chapter",
        default=None,
        help="要检查的章节文件（ch-001 / ch-001.md / draft/chapters/ch-001.md）；不填则检查最新 ch-*.md",
    )
    parser.add_argument("--default-min", type=int, default=3000, help="未读到配置时的默认最小字数（默认：3000）")
    parser.add_argument("--verbose", action="store_true", help="即使密度未超阈值也列出所有命中（调试用）")
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

    print("[INFO] 文件：", chapter_path)
    if config_path.exists():
        print("[INFO] 配置：", config_path)
    else:
        print("[WARN] 未找到配置：", config_path)
    print(f"[INFO] 字数（粗略，不含空白）：{char_count}")
    print(f"[INFO] 门槛：min={min_len}" + (f", max={max_len}" if max_len is not None else "") + (f", target={target_len}" if target_len is not None else ""))

    ok = True

    # ── 1. 字数检查 ──
    if char_count < min_len:
        ok = False
        print(f"[FAIL] 字数不足：还差 {min_len - char_count}")
    if max_len is not None and char_count > max_len:
        ok = False
        print(f"[FAIL] 字数超上限：超出 {char_count - max_len}")

    # ── 2. 硬性禁止（零容忍） ──
    forbidden_hits = find_forbidden_hits(text)
    if forbidden_hits:
        ok = False
        print(f"[FAIL] 索引/系统提示泄露（{len(forbidden_hits)} 处）：")
        for h in forbidden_hits[:30]:
            print(f"  L{h.line_no} [{h.kind}]: {h.line}")

    # ── 3. AI 味密度检测 ──
    ai_hits = find_ai_flavor_hits(text)
    if ai_hits:
        by_cat, levels = compute_density_report(ai_hits, char_count)
        k = max(char_count / 1000.0, 0.5)

        has_fail = any(v == "fail" for v in levels.values())
        has_warn = any(v == "warn" for v in levels.values())

        if has_fail or has_warn:
            print(f"\n[AI 味分析] 总命中 {len(ai_hits)} 处（{len(ai_hits)/k:.1f}/千字）：")
            print()

        for cat in sorted(by_cat.keys(), key=lambda c: {"fail": 0, "warn": 1, "ok": 2}[levels[c]]):
            hits_list = by_cat[cat]
            level = levels[cat]
            narr_count = sum(1 for h in hits_list if not h.in_dialogue)
            dlg_count = sum(1 for h in hits_list if h.in_dialogue)
            density = narr_count / k

            if level == "ok" and not args.verbose:
                continue

            tag = "[FAIL]" if level == "fail" else "[WARN]"
            if level == "fail":
                ok = False

            detail = f"叙述 {narr_count} 处"
            if dlg_count:
                detail += f" + 对白 {dlg_count} 处（不计入密度）"
            print(f"  {tag} {cat}：{detail}，密度 {density:.1f}/千字")

            # 展示命中明细（同级别最多展示 5 条，避免刷屏）
            shown = 0
            for h in hits_list:
                if shown >= 5:
                    remaining = len(hits_list) - shown
                    print(f"        ...另有 {remaining} 处省略")
                    break
                dlg_mark = " [对白]" if h.in_dialogue else ""
                print(f"        L{h.line_no}{dlg_mark}: {h.line[:80]}")
                if shown == 0:
                    print(f"        → 建议: {h.suggestion}")
                shown += 1
            print()

        if not has_fail and not has_warn:
            if args.verbose:
                print(f"\n[INFO] AI 味命中 {len(ai_hits)} 处，但密度均在正常范围内。")
    else:
        pass  # 无命中不输出，减少噪音

    # ── 汇总 ──
    if ok:
        print("[OK] 通过。")
        return 0

    return 2


if __name__ == "__main__":
    raise SystemExit(main())
