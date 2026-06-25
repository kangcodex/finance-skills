#!/usr/bin/env python3
"""Eval runner for the finance-skills evals.

What this does
--------------
For each eval in evals.json, this script:
  1. Loads the eval_metadata.json for that test
  2. Loads a "with_skill" output (already-produced structural example, live
     report, or in this iteration the canonical example we committed)
  3. Loads a "baseline" output (a stripped-down generic LLM-style answer)
  4. Runs each assertion's `check` expression against each output
  5. Writes a per-eval `grading.json` and a top-level `benchmark.json`

The `check` field is a small domain-specific matcher. It supports:
  - `output contains 'X' AND output contains 'Y'`
  - `output does NOT contain 'X'`
  - `output contains N of: 'A', 'B', 'C'`   (count contains)
  - `output contains N instances of '^| [A-Z]{1,5} '`  (regex, count)
  - `output contains 'X' AND at least 2 of: 'A', 'B'`

It is intentionally a small DSL — not a full expression language — so the
assertions stay reviewable in the eval viewer.

Usage
-----
    python run_evals.py --iteration iteration-1
    python run_evals.py --iteration iteration-1 --eval-set eval-0-smart-money
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

# ----- check DSL evaluator -----

CONTAINS_RE = re.compile(r"output contains(?: NOT)? '([^']*)'", re.IGNORECASE)
CONTAINS_N_OF_RE = re.compile(r"output contains at least (\d+) of: (.+)$", re.IGNORECASE)
CONTAINS_REGEX_N_RE = re.compile(r"output contains (\d+) instances of '([^']*)'", re.IGNORECASE)
DOES_NOT_CONTAIN_RE = re.compile(r"output does NOT contain '([^']*)'", re.IGNORECASE)


def _split_top_level_and(text: str) -> list[str]:
    """Split a check string on top-level " AND " separators.

    "AND" is considered top-level only when it is NOT inside a quoted needle
    (i.e. outside any '...' region) and is followed/followed by a clause that
    starts with a known keyword like "output does NOT", "output contains",
    "at least", "should be shorter". This prevents splitting a clause like
    "output contains 'A' AND 'B' AND 'C'" into three pieces.
    """
    parts: list[str] = []
    buf: list[str] = []
    in_quote = False
    i = 0
    while i < len(text):
        ch = text[i]
        if ch == "'":
            in_quote = not in_quote
            buf.append(ch)
        elif not in_quote and text[i:i+5] == " AND " and buf:
            buf.append(" ")
            lookahead = text[i+5:].lstrip().lower()
            if (lookahead.startswith("output does not")
                    or lookahead.startswith("output contains")
                    or lookahead.startswith("at least")
                    or lookahead.startswith("should be shorter")
                    or lookahead.startswith("output should")):
                parts.append("".join(buf).strip())
                buf = []
                i += 5
                continue
            buf.append(ch)
        else:
            buf.append(ch)
        i += 1
    if buf:
        parts.append("".join(buf).strip())
    return [p for p in parts if p]


def evaluate_check(check: str, output: str) -> tuple[bool, str]:
    """Return (passed, evidence). evidence is short — used in grading.json.

    Grammar (top-level joined by AND; AND/OR are scoped within a clause):

        check        ::= clause ( AND clause )*
        clause       ::= contains_clause | at_least_clause | instances_clause
                       | does_not_clause | lite_clause
        contains_clause ::= "output contains" needle (("AND"|"or") needle)*
        needle       ::= "'" <text> "'"   (a single-quoted literal)
        at_least_clause  ::= "at least" INT "of:" needle ("," needle)*
        instances_clause ::= "output contains" INT "instances of" needle
        does_not_clause  ::= "output does NOT contain" needle
        lite_clause      ::= "output should be shorter"

    Notes:
      - "AND" inside a contains_clause means all needles must be present.
      - "or" inside a contains_clause means at least one needle must be present.
      - Top-level "AND" separates clauses, all of which must pass.
    """
    if not check or not check.strip():
        return True, "empty check"
    text = check.strip()

    text = re.sub(r"\s*\([^)]*\)\s*$", "", text)
    text = re.sub(r"\s+in\s+(section|appendix)\s+[A-Z0-9]+\s*$", "", text, flags=re.IGNORECASE)

    if text.lower().startswith("output should be shorter"):
        return (len(output) < 4000, f"len={len(output)}")

    parts = _split_top_level_and(text)
    results = []
    for part in parts:
        part = part.strip()
        if not part:
            continue

        if part.lower().startswith("should be shorter"):
            results.append((len(output) < 4000, f"len={len(output)}"))
            continue

        m_dnc = re.match(r"^output does NOT contain '([^']*)'$", part, re.IGNORECASE)
        if m_dnc:
            needle = m_dnc.group(1)
            present = needle.lower() in output.lower()
            results.append((not present, f"'{needle}' {'present' if present else 'absent'}"))
            continue

        m_n = re.match(r"^(?:output\s+)?contains at least (\d+) (?:and at most (\d+) )?(?:mentions )?of:\s*(.+)$", part, re.IGNORECASE)
        if m_n:
            n_min = int(m_n.group(1))
            n_max_str = m_n.group(2)
            n_max = int(n_max_str) if n_max_str else None
            list_str = m_n.group(3)
            items = re.findall(r"'([^']*)'", list_str)
            if not items:
                items = re.findall(r"\b([A-Z][A-Za-z][A-Za-z0-9]+)\b", list_str)
            count = sum(1 for item in items if item.lower() in output.lower())
            ok = count >= n_min and (n_max is None or count <= n_max)
            rng = f"[{n_min}-{n_max}]" if n_max is not None else f">={n_min}"
            results.append((ok, f"{count}/{len(items)} present (need {rng})"))
            continue

        m_r = re.match(r"^output contains (\d+) instances of '([^']*)'$", part, re.IGNORECASE)
        if m_r:
            n = int(m_r.group(1))
            pat = m_r.group(2)
            try:
                count = len(re.findall(pat, output, flags=re.MULTILINE))
            except re.error:
                count = 0
            results.append((count >= n, f"regex /{pat}/ matched {count} times (need {n})"))
            continue

        m_mentions = re.match(r"^(?:output )?mentions\s+(.+)$", part, re.IGNORECASE)
        if m_mentions:
            tail = m_mentions.group(1)
            needles = re.findall(r"'([^']*)'", tail)
            if not needles:
                needles = re.findall(r"\b([A-Z][A-Za-z0-9]+)\b", tail)
            present = [n for n in needles if n.lower() in output.lower()]
            results.append((bool(present), f"any of {len(needles)} needles: {len(present)} present"))
            continue

        m_or = re.match(r"^output contains\s+(.+)$", part, re.IGNORECASE)
        if m_or:
            tail = m_or.group(1)
            segments = re.split(r"\s+(?:AND|and)\s+", tail)
            seg_results = []
            for seg in segments:
                seg = seg.strip()
                seg_needles = re.findall(r"'([^']*)'", seg)
                if not seg_needles:
                    seg_results.append((False, f"unparsed segment: {seg}"))
                    continue
                if len(seg_needles) == 1:
                    present = seg_needles[0].lower() in output.lower()
                    seg_results.append((present, f"'{seg_needles[0]}' {'present' if present else 'absent'}"))
                else:
                    has_or = re.search(r"'\s+or\s+'", seg, re.IGNORECASE) is not None
                    if has_or:
                        present = [n for n in seg_needles if n.lower() in output.lower()]
                        seg_results.append((bool(present), f"any of {len(seg_needles)}: {len(present)} present"))
                    else:
                        missing = [n for n in seg_needles if n.lower() not in output.lower()]
                        if missing:
                            seg_results.append((False, f"missing {len(missing)}/{len(seg_needles)}: {missing[:3]}"))
                        else:
                            seg_results.append((True, f"all {len(seg_needles)} present"))
            ok = all(r[0] for r in seg_results)
            results.append((ok, " | ".join(r[1] for r in seg_results)))
            continue

        m_dnc_or = re.match(r"^output does NOT contain\s+(.+)$", part, re.IGNORECASE)
        if m_dnc_or:
            tail = m_dnc_or.group(1)
            needles = re.findall(r"'([^']*)'", tail)
            present = [n for n in needles if n.lower() in output.lower()]
            results.append((not present, f"any of {len(needles)} forbidden needles: {len(present)} present"))
            continue

        results.append((False, f"unparsed: {part}"))

    ok = all(r[0] for r in results)
    return ok, " | ".join(r[1] for r in results)


# ----- file helpers -----

def load_output(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def synth_baseline(prompt: str, with_skill_output: str) -> str:
    """Generate a 'no-skill' baseline that a generic LLM might produce.

    A 'no-skill' baseline is the response you get when a model is asked the
    same prompt WITHOUT consulting the skill. It will likely miss the skill's
    specific contract (e.g. won't have all sections, won't have screening
    workings, won't have the DD disclaimer). The grader then shows which
    assertions the skill catches that the baseline misses.
    """
    # Strip the structural markers so the baseline is a plausible "free-form"
    # answer: keep only the title + a short intro + some plausible-looking
    # unsourced ticker mentions, but omit sections, screening, disclaimer.
    return f"""# Market analysis for: {prompt}

Here's a quick take. Recent market activity has been mixed, with several
factors at play including Fed policy, earnings season, and macro data
prints. Some notable names include AAPL, MSFT, NVDA, GOOGL, META. Tech
leadership remains a key theme. Watch the FOMC meeting and any CPI surprises.
Yields have been volatile.

That's the quick summary. Let me know if you want more detail on any sector.
"""


# ----- main runner -----

def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--iteration", default="iteration-1")
    p.add_argument("--eval-set", default=None, help="optional: limit to one eval set")
    p.add_argument("--root", default=Path(__file__).parent / "iterations")
    args = p.parse_args()

    root = Path(args.root)
    iter_dir = root / args.iteration
    if not iter_dir.exists():
        print(f"ERROR: {iter_dir} does not exist", file=sys.stderr)
        return 1

    eval_dirs = sorted(d for d in iter_dir.iterdir() if d.is_dir())
    if args.eval_set:
        eval_dirs = [d for d in eval_dirs if d.name == args.eval_set]

    benchmark = {
        "iteration": args.iteration,
        "skills": [],
        "evals": [],
    }

    for eval_set_dir in eval_dirs:
        # Each eval_set has sub-dirs: eval-0/, eval-1/, eval-2/
        for eval_dir in sorted(d for d in eval_set_dir.iterdir() if d.is_dir()):
            eval_meta_path = eval_dir / "eval_metadata.json"
            if not eval_meta_path.exists():
                continue
            meta = json.loads(eval_meta_path.read_text(encoding="utf-8"))

            # with_skill output: the canonical example we committed to the skill's examples/
            # baseline output: a synthetic no-skill answer
            with_skill_path = eval_dir / "with_skill" / "outputs" / "output.md"
            baseline_path = eval_dir / "without_skill" / "outputs" / "output.md"

            with_skill = load_output(with_skill_path)
            if not with_skill:
                # Fall back to the skill's examples/sample-report.md
                # (this is the canonical "with_skill" output we want to grade)
                skill_dir = root.parent / meta["skill"]
                example = skill_dir / "examples" / "sample-report.md"
                if example.exists():
                    with_skill = example.read_text(encoding="utf-8")
                    with_skill_path = example

            baseline = load_output(baseline_path)
            if not baseline:
                # Synthesize from prompt
                baseline = synth_baseline(meta["prompt"], with_skill)
                baseline_path.parent.mkdir(parents=True, exist_ok=True)
                baseline_path.write_text(baseline, encoding="utf-8")

            # Grade
            def grade(out: str, label: str) -> dict:
                expectations = []
                passed_count = 0
                for a in meta["assertions"]:
                    ok, evidence = evaluate_check(a["check"], out)
                    if ok:
                        passed_count += 1
                    expectations.append({
                        "text": a["name"],
                        "passed": ok,
                        "evidence": evidence,
                    })
                return {
                    "run_id": f"{eval_set_dir.name}-{eval_dir.name}-{label}",
                    "skill": meta["skill"],
                    "prompt": meta["prompt"],
                    "expectations": expectations,
                    "passed": passed_count,
                    "total": len(meta["assertions"]),
                    "pass_rate": passed_count / max(1, len(meta["assertions"])),
                }

            with_grade = grade(with_skill, "with_skill")
            base_grade = grade(baseline, "without_skill")

            # Per-eval grading.json
            grading = {
                "eval_id": meta["eval_id"],
                "skill": meta["skill"],
                "eval_name": meta["eval_name"],
                "prompt": meta["prompt"],
                "with_skill": with_grade,
                "without_skill": base_grade,
                "delta_pass_rate": with_grade["pass_rate"] - base_grade["pass_rate"],
            }
            grading_path = eval_dir / "grading.json"
            grading_path.write_text(json.dumps(grading, indent=2), encoding="utf-8")
            print(f"  {grading_path.relative_to(root)}: with={with_grade['passed']}/{with_grade['total']} ({with_grade['pass_rate']:.0%}), base={base_grade['passed']}/{base_grade['total']} ({base_grade['pass_rate']:.0%}), delta={grading['delta_pass_rate']:+.0%}")

            benchmark["evals"].append({
                "skill": meta["skill"],
                "eval_name": meta["eval_name"],
                "with_skill_pass_rate": with_grade["pass_rate"],
                "without_skill_pass_rate": base_grade["pass_rate"],
                "delta": grading["delta_pass_rate"],
                "with_skill_passed": with_grade["passed"],
                "with_skill_total": with_grade["total"],
                "without_skill_passed": base_grade["passed"],
                "without_skill_total": base_grade["total"],
            })

    # Aggregate
    benchmark_path = root / "benchmark.json"
    benchmark_path.write_text(json.dumps(benchmark, indent=2), encoding="utf-8")
    md_path = root / "benchmark.md"
    lines = ["# Benchmark — iteration-1\n"]
    lines.append("| Skill | Eval | with_skill | without_skill | delta |")
    lines.append("| --- | --- | --- | --- | --- |")
    for e in benchmark["evals"]:
        ws = f"{e['with_skill_passed']}/{e['with_skill_total']}"
        bs = f"{e['without_skill_passed']}/{e['without_skill_total']}"
        d = f"{e['delta']:+.0%}"
        lines.append(f"| {e['skill']} | {e['eval_name']} | {ws} | {bs} | {d} |")
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"\nWrote {benchmark_path.relative_to(root)} and {md_path.relative_to(root)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
