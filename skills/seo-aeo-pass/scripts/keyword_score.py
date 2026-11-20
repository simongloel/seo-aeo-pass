#!/usr/bin/env python3
"""Rank keyword candidates by what a ranking would be worth, not by search volume.

Input: a CSV with a header row. Only `term` is required; use what you have.
  term               the search term
  volume             monthly searches (from a tool, with its name in `source`); leave empty if unknown
  signal             strong | some | weak, when there is no measured volume
  impressions        Search Console impressions (28 days) if the site already shows up
  cpc                cost per click in your currency (tool or Keyword Planner)
  kd                 keyword difficulty 0-100 from a tool, or a DIY estimate (references/metrics.md)
  intent             transactional | commercial | informational | navigational
  business_potential 0-3: 3 = the product is the answer, 2 = it helps a lot, 1 = can be mentioned, 0 = no fit
  aio                yes if an AI Overview / AI answer shows for the term
  position           current position if the site ranks already
  effort             S | M | L (new page from scratch = M, rework = S, needs a product change = L)
  source             where volume/kd/cpc came from, with date

Model (ours, inferred, documented in references/metrics.md; not a vendor formula):
  position used      the current position when the site ranks (never a better guess); else
                     a position estimated from kd against --authority (same 0-100 scale, e.g.
                     a tool's authority next to the same tool's KD); no kd and no position = not estimated
  monthly visits     volume x CTR(position), CTR cut by --aio-factor when an AI answer shows.
                     Search Console impressions stand in for volume when there is none
                     (28-day count x 30/28; a floor, since the site isn't shown for every search)
  value per visit    --conv-rate x --conv-value when given, else CPC (a ceiling, not your value)
  priority           visits x value per visit x intent weight x business_potential/3 / effort
  upside             with --target-pos N: the same value if the page reached position N, shown
                     as a separate "if" column, never as the expectation

Terms without volume, impressions or a position estimate get a relative score from the
signal column and are listed separately. Never present a relative score as money.

  keyword_score.py candidates.csv --authority 15 --conv-rate 0.02 --conv-value 120
  keyword_score.py candidates.csv --authority 30 --out scored.csv
"""
import argparse
import csv
import math
import sys

# Organic CTR by position, desktop+mobile blend without AI answer. Backlinko 2023 (4M results) for 1-3,
# smoothed to a power curve below; see references/metrics.md for the other curves and why they differ.
CTR = {1: 0.276, 2: 0.158, 3: 0.110, 4: 0.084, 5: 0.063, 6: 0.049, 7: 0.039, 8: 0.033, 9: 0.027, 10: 0.024}
INTENT_W = {"transactional": 1.0, "commercial": 0.8, "informational": 0.3, "navigational": 0.05, "": 0.5}
SIGNAL = {"strong": 3, "some": 2, "weak": 1, "": 0}
EFFORT = {"S": 1, "M": 2, "L": 4, "": 2}


def ctr(pos):
    if pos <= 10:
        return CTR[max(1, round(pos))]
    return 0.024 * (10 / pos) ** 2.5  # page two and beyond: almost nothing


def expected_position(kd, authority, current):
    """The current position if the site ranks; else a heuristic from kd vs authority; else None."""
    if current:
        return current, "current"
    if kd is None:
        return None, "unknown"
    gap = kd - authority
    return (3 if gap <= 0 else 6 if gap <= 15 else 12 if gap <= 30 else 25 if gap <= 50 else 50), "estimated"


def num(v):
    try:
        return float(str(v).replace(",", ".").replace("€", "").replace("$", "").strip())
    except ValueError:
        return None


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("csv")
    ap.add_argument("--authority", type=float, default=10, help="the site's authority, 0-100, same scale as kd")
    ap.add_argument("--conv-rate", type=float, help="visitor-to-customer rate for organic visits, e.g. 0.02")
    ap.add_argument("--conv-value", type=float, help="value of one conversion (first-year revenue x margin, or order value)")
    ap.add_argument("--aio-factor", type=float, default=0.5, help="CTR multiplier when an AI answer shows (default 0.5; studies give 0.4-0.6)")
    ap.add_argument("--target-pos", type=float, help="also show the value if the page reached this position")
    ap.add_argument("--out", help="write the scored CSV here")
    args = ap.parse_args()

    with open(args.csv, encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
    if not rows or "term" not in rows[0]:
        sys.exit("CSV needs a header row with at least a `term` column")

    vpv_mode = "conversion" if args.conv_rate and args.conv_value else "cpc"
    for r in rows:
        g = lambda k: (r.get(k) or "").strip()
        volume, cpc, kd, cur, impr = num(g("volume")), num(g("cpc")), num(g("kd")), num(g("position")), num(g("impressions"))
        intent = g("intent").lower()
        bp = num(g("business_potential"))
        bp = 2 if bp is None else max(0, min(3, bp))
        aio = args.aio_factor if g("aio").lower() in ("yes", "y", "1", "true") else 1
        pos, pos_basis = expected_position(kd, args.authority, cur)
        vpv = args.conv_rate * args.conv_value if vpv_mode == "conversion" else (cpc if cpc is not None else 1.0)
        weight = INTENT_W.get(intent, 0.5) * bp / 3 / EFFORT.get(g("effort").upper(), 2)
        if volume is not None:
            basis = f"volume ({g('source') or 'source not given'})"
        elif impr is not None:
            volume, basis = impr * 30 / 28, "GSC impressions (floor)"
        else:
            basis = ""
        r["vpv_note"] = vpv_mode if vpv_mode == "conversion" or cpc is not None else "cpc unknown: 1.0 used, value is not money"
        if volume is not None and pos is not None:
            visits = volume * ctr(pos) * aio
            r.update(position=f"{pos:g} ({pos_basis})", visits_month=f"{visits:.1f}", value_month=f"{visits * vpv:.2f}",
                     priority=f"{visits * vpv * weight:.2f}", basis=basis)
            if args.target_pos and pos > args.target_pos:
                r["if_target"] = f"{volume * ctr(args.target_pos) * aio * vpv:.2f} at pos {args.target_pos:g}"
        else:
            pts = SIGNAL.get(g("signal").lower(), 0) * (cpc if cpc is not None else 1.0)
            why = "no volume or impressions" if volume is None else "no position estimate (needs kd or a current position)"
            r.update(position="" if pos is None else f"{pos:g} ({pos_basis})", visits_month="", value_month="",
                     priority=f"{pts * weight:.2f}", basis=f"relative: {why}")

    measured = sorted([r for r in rows if not r["basis"].startswith("relative")], key=lambda r: -float(r["priority"]))
    relative = sorted([r for r in rows if r["basis"].startswith("relative")], key=lambda r: -float(r["priority"]))
    print(f"# value per visit: {vpv_mode}; authority {args.authority:g}; AI-answer CTR factor {args.aio_factor:g}\n")
    if measured:
        print("| term | volume | kd | intent | position used | visits/mo | value/mo | priority | upside | basis |")
        print("|---|---|---|---|---|---|---|---|---|---|")
        for r in measured:
            print(f"| {r['term']} | {r.get('volume') or r.get('impressions', '')} | {r.get('kd', '')} | {r.get('intent', '')} | "
                  f"{r['position']} | {r['visits_month']} | {r['value_month']} | {r['priority']} | {r.get('if_target', '')} | "
                  f"{r['basis']}{'; ' + r['vpv_note'] if 'unknown' in r['vpv_note'] else ''} |")
    if relative:
        print("\n## relative order only, not money\n\n| term | signal | cpc | intent | priority (relative) | why |\n|---|---|---|---|---|---|")
        for r in relative:
            print(f"| {r['term']} | {r.get('signal', '')} | {r.get('cpc', '')} | {r.get('intent', '')} | {r['priority']} | {r['basis'][10:]} |")
    if args.out:
        fields = list(dict.fromkeys(k for r in rows for k in r))
        with open(args.out, "w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=fields)
            w.writeheader()
            w.writerows(measured + relative)


if __name__ == "__main__":
    main()
