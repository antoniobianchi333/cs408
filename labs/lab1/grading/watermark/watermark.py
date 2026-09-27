#!/usr/bin/env python3
"""Plant and check zero-width watermarks in the Project 1 skeleton.

The watermark lives in the file-header comment blocks of grammar.py and
project/magic/magic.c -- two files the handout does not ask students to modify.
Markers sit mid-line between words in unindented comment lines. That placement
is the one that survived reliably when the Spring 2026 watermark was measured
across all 50 lab2 group repositories: markers in indented comment blocks and
at line ends were lost by every anomalous group regardless of cause, while
markers in unindented top-level comments survived everywhere.

Usage:
    watermark.py plant <skeleton-dir> [--payload CODE]
    watermark.py check <skeleton-dir> [--json]

`plant` is idempotent: it strips any existing header block and marker before
writing, so re-running with a different payload is safe.
"""

import argparse
import json
import os
import re
import sys

# Marker alphabet. Three symbols, deliberately: in Spring 2026 one group lost
# precisely every U+200B and kept every U+200C/U+200D, which identified a
# ZWSP-stripping tool rather than a rewrite. A single-symbol watermark cannot
# make that distinction.
SYMBOLS = ["​", "‌", "‍"]
SYMBOL_NAMES = {"​": "ZWSP", "‌": "ZWNJ", "‍": "ZWJ"}
ZW_RE = re.compile("[​‌‍]")

# Slots are written as {} in the templates below. Every slot is mid-line
# between two words in a column-0 comment line: never at end of line (editors
# that trim trailing whitespace remove those) and never inside an indented
# block (re-indenting formatters rewrite those).

GRAMMAR_HEADER = """\
# -------------------------------------------------------------------------- #
# grammar.py -- parser {}for the context-free grammar files under project/.
#
# A grammar file is a {}sequence of rules, each one terminated by a semicolon:
#
#     rule = nonterminal "=" ( terminal | nonterminal )* ";"
#
# Nonterminals are bare {}identifiers. Terminals are double-quoted strings and
# may contain the usual {}escapes, which are decoded when the rule is parsed.
#
# parse_cfg() returns a {}CFGGrammar whose rules carry a rule id (rid) assigned
# in source order, so you {}can use it to index back into the grammar.
#
# This file is provided {}for you and you should not need to change it.
# -------------------------------------------------------------------------- #

"""

MAGIC_HEADER = """\
// -------------------------------------------------------------------------- //
// magic.c -- a fuzzing {}target guarded by nested magic-byte checks.
//
// vulnerable_function() {}below is protected by four layers of exact-match
// comparisons against the {}input. Reaching the crash needs 15 specific bytes,
// which random mutation {}alone is very unlikely to produce.
//
// Use this target to see {}whether your greybox fuzzer makes progress through
// deep and narrow conditions, {}for instance by recovering the constants used
// in the comparisons above.
//
// This file is one of the {}targets we fuzz during grading; do not change it.
// -------------------------------------------------------------------------- //

"""

TARGETS = {
    "grammar.py": GRAMMAR_HEADER,
    os.path.join("project", "magic", "magic.c"): MAGIC_HEADER,
}

# How many chars of preceding text identify a slot when checking. Long enough
# to be unique, short enough to survive small edits elsewhere on the line.
ANCHOR = 22


def _slots(template):
    """Yield (anchor_text, slot_index) for each {} in a template."""
    clean = template.replace("{}", "")
    out, cursor, idx = [], 0, 0
    for part in template.split("{}")[:-1]:
        cursor += len(part)
        out.append((clean[max(0, cursor - ANCHOR):cursor], idx))
        idx += 1
    return out


def _header_bounds(text, template):
    """Locate an already-planted header, returning (start, end) or None."""
    rule = template.split("\n")[0]
    if not text.startswith(rule):
        return None
    end = text.find(rule, len(rule))
    if end < 0:
        return None
    end += len(rule)
    while end < len(text) and text[end] == "\n":
        end += 1
    return (0, end)


def _encode(payload, n_slots):
    """Spread payload over n_slots as base-3 digits, repeated for redundancy."""
    value = 0
    for ch in payload.encode("utf-8"):
        value = value * 257 + ch
    digits = []
    v = value
    for _ in range(max(1, n_slots // 3)):
        digits.append(v % 3)
        v //= 3
    return [digits[i % len(digits)] for i in range(n_slots)]


def plant(root, payload):
    changed = []
    for rel, template in TARGETS.items():
        path = os.path.join(root, rel)
        if not os.path.exists(path):
            print(f"  skip (missing): {rel}", file=sys.stderr)
            continue
        text = open(path, encoding="utf-8").read()
        bounds = _header_bounds(text, template)
        body = text[bounds[1]:] if bounds else text
        body = ZW_RE.sub("", body)

        n = template.count("{}")
        header = template
        for digit in _encode(payload, n):
            header = header.replace("{}", SYMBOLS[digit], 1)
        open(path, "w", encoding="utf-8").write(header + body)
        changed.append((rel, n))
    return changed


def check(root):
    report = {}
    for rel, template in TARGETS.items():
        path = os.path.join(root, rel)
        entry = {"present": 0, "missing": 0, "slots": [], "header": True}
        if not os.path.exists(path):
            entry["header"] = False
            entry["error"] = "file missing"
            report[rel] = entry
            continue
        text = open(path, encoding="utf-8").read()
        stripped = ZW_RE.sub("", text)
        if not stripped.startswith(template.split("\n")[0]):
            entry["header"] = False

        for anchor, idx in _slots(template):
            # Find the anchor in the zero-width-stripped text, then map that
            # position back into the original to see what symbol follows.
            pos = stripped.find(anchor)
            found = None
            if pos >= 0:
                target = pos + len(anchor)
                seen = 0
                for i, ch in enumerate(text):
                    if seen == target:
                        found = ch if ch in SYMBOL_NAMES else None
                        break
                    if not ZW_RE.match(ch):
                        seen += 1
            entry["slots"].append(
                {"i": idx, "anchor": anchor.strip(),
                 "symbol": SYMBOL_NAMES.get(found) if found else None,
                 "anchor_found": pos >= 0}
            )
            if found:
                entry["present"] += 1
            else:
                entry["missing"] += 1
        report[rel] = entry
    return report


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("plant", help="write header blocks and plant markers")
    p.add_argument("root")
    p.add_argument("--payload", default="TEMPLATE",
                   help="code to encode, e.g. a group name (default: TEMPLATE)")
    c = sub.add_parser("check", help="report which markers survive")
    c.add_argument("root")
    c.add_argument("--json", action="store_true")
    args = ap.parse_args()

    if args.cmd == "plant":
        for rel, n in plant(args.root, args.payload):
            print(f"  planted {n} markers in {rel}")
        return 0

    report = check(args.root)
    if args.json:
        print(json.dumps(report, indent=2))
        return 0

    total_present = total = 0
    for rel, e in report.items():
        if "error" in e:
            print(f"{rel}: {e['error']}")
            continue
        n = e["present"] + e["missing"]
        total_present += e["present"]
        total += n
        head = "header intact" if e["header"] else "HEADER BLOCK GONE"
        print(f"\n{rel}: {e['present']}/{n} markers, {head}")
        for s in e["slots"]:
            if s["symbol"]:
                continue
            why = "anchor text gone" if not s["anchor_found"] else "text kept, marker stripped"
            print(f"    slot {s['i']} missing ({why}): ...{s['anchor']}")
    print(f"\nTOTAL: {total_present}/{total} markers present")
    return 0 if total_present == total else 1


if __name__ == "__main__":
    sys.exit(main())
