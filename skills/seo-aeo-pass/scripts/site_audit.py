#!/usr/bin/env python3
"""Crawl a site from its sitemap and report what a paid audit tool reports.

Standard library only. Reads sitemap.xml (and sitemap indexes), fetches every
page, and checks per page: status, redirect, noindex, canonical, title and
description (missing, length, duplicates), H1 count, title equal to H1, lang
and hreflang partners, structured data types, word count, internal links out,
internal links in (pages nobody links to, pages with one link), links to pages
that do not answer 200, and pages linked internally but missing in the sitemap.

  site_audit.py https://example.com/sitemap.xml --out audit.json
  site_audit.py https://example.com/sitemap.xml --limit 200 --include /de/

Prints a summary by issue with example URLs; --out keeps every page's row so
the next run can be compared with it.
"""
import argparse
import collections
import concurrent.futures as cf
import html
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

UA = "Mozilla/5.0 (compatible; seo-aeo-pass-audit/1.0)"
TITLE_MAX = 70      # characters, what search results show before cutting
DESC_MIN, DESC_MAX = 70, 160


def fetch(url, timeout=20):
    """Returns (status, final_url, headers, text). Never raises."""
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "text/html,application/xml;q=0.9,*/*;q=0.8"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as res:
            body = res.read(3_000_000)
            charset = res.headers.get_content_charset() or "utf-8"
            return res.status, res.geturl(), dict(res.headers), body.decode(charset, "replace")
    except urllib.error.HTTPError as err:
        return err.code, url, dict(err.headers or {}), ""
    except Exception as err:
        return 0, url, {"error": str(err)}, ""


def sitemap_urls(url, seen=None):
    seen = seen or set()
    if url in seen:
        return []
    seen.add(url)
    status, _, _, text = fetch(url)
    if status != 200:
        print(f"sitemap {url} answered {status}", file=sys.stderr)
        return []
    locs = [html.unescape(m) for m in re.findall(r"<loc>\s*(.*?)\s*</loc>", text, re.S)]
    if "<sitemapindex" in text:
        out = []
        for loc in locs:
            out += sitemap_urls(loc, seen)
        return out
    return locs


def strip_tags(s):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", s))).strip()


def attr(tag, name):
    m = re.search(rf'{name}\s*=\s*"([^"]*)"|{name}\s*=\s*\'([^\']*)\'', tag, re.I)
    return html.unescape(m.group(1) if m and m.group(1) is not None else (m.group(2) if m else "")) if m else ""


def norm(url):
    u = urllib.parse.urlsplit(url)
    path = u.path or "/"
    return urllib.parse.urlunsplit((u.scheme, u.netloc.lower(), path, "", ""))


def analyse(url):
    status, final, headers, text = fetch(url)
    row = {"url": url, "status": status, "final": final if norm(final) != norm(url) else "", "issues": []}
    if status != 200 or not text:
        row["issues"].append(f"status {status}")
        return row
    head = text[: text.lower().find("</head>") + 7] if "</head>" in text.lower() else text[:20000]
    body = re.sub(r"<script.*?</script>|<style.*?</style>|<noscript.*?</noscript>", " ", text, flags=re.S | re.I)

    title = strip_tags(m.group(1)) if (m := re.search(r"<title[^>]*>(.*?)</title>", head, re.S | re.I)) else ""
    metas = re.findall(r"<meta\b[^>]*>", head, re.I)
    desc = next((attr(t, "content") for t in metas if attr(t, "name").lower() == "description"), "")
    robots = " ".join(attr(t, "content").lower() for t in metas if attr(t, "name").lower() in ("robots", "googlebot"))
    robots += " " + headers.get("X-Robots-Tag", "").lower()
    links_head = re.findall(r"<link\b[^>]*>", head, re.I)
    canonical = next((attr(t, "href") for t in links_head if attr(t, "rel").lower() == "canonical"), "")
    hreflang = {attr(t, "hreflang").lower(): attr(t, "href") for t in links_head if attr(t, "hreflang")}
    lang = attr(m.group(0), "lang") if (m := re.search(r"<html\b[^>]*>", text, re.I)) else ""
    h1s = [strip_tags(h) for h in re.findall(r"<h1\b[^>]*>(.*?)</h1>", body, re.S | re.I)]
    words = len(strip_tags(re.sub(r"<(header|footer|nav)\b.*?</\1>", " ", body, flags=re.S | re.I)).split())

    types = []
    for block in re.findall(r'<script[^>]*type="application/ld\+json"[^>]*>(.*?)</script>', text, re.S | re.I):
        try:
            def walk(node):
                if isinstance(node, dict):
                    t = node.get("@type")
                    types.extend(t if isinstance(t, list) else [t] if t else [])
                    for v in node.values():
                        walk(v)
                elif isinstance(node, list):
                    for v in node:
                        walk(v)
            walk(json.loads(block))
        except Exception:
            row["issues"].append("structured data is not valid JSON")

    host = urllib.parse.urlsplit(url).netloc.lower()
    internal, empty_anchor = set(), 0
    for m in re.finditer(r"<a\b([^>]*)>(.*?)</a>", body, re.S | re.I):
        href = attr(m.group(1), "href")
        if not href or href.startswith(("#", "mailto:", "tel:", "javascript:")):
            continue
        target = urllib.parse.urljoin(url, href)
        if urllib.parse.urlsplit(target).netloc.lower() != host:
            continue
        internal.add(norm(target))
        if not strip_tags(m.group(2)) and not attr(m.group(1), "aria-label") and "alt=" not in m.group(2).lower():
            empty_anchor += 1

    row.update(title=title, description=desc, h1=h1s[:3], lang=lang, canonical=canonical, hreflang=hreflang,
               noindex="noindex" in robots, words=words, types=sorted(set(types)), links=sorted(internal))
    issues = row["issues"]
    if "noindex" in robots:
        issues.append("noindex but in the sitemap")
    if not title:
        issues.append("no title")
    elif len(title) > TITLE_MAX:
        issues.append(f"title over {TITLE_MAX} characters")
    if not desc:
        issues.append("no description")
    elif len(desc) > DESC_MAX:
        issues.append(f"description over {DESC_MAX} characters")
    elif len(desc) < DESC_MIN:
        issues.append(f"description under {DESC_MIN} characters")
    if not h1s:
        issues.append("no h1")
    elif len(h1s) > 1:
        issues.append("more than one h1")
    if not canonical:
        issues.append("no canonical")
    elif norm(canonical) != norm(url):
        issues.append("canonical points elsewhere")
    if hreflang and norm(url) not in {norm(v) for v in hreflang.values()}:
        issues.append("hreflang set does not name the page itself")
    if words < 200:
        issues.append("under 200 words")
    if empty_anchor:
        issues.append("link without text")
    if row["final"]:
        issues.append("sitemap URL redirects")
    return row


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("sitemap")
    ap.add_argument("--limit", type=int, default=0, help="audit at most this many pages")
    ap.add_argument("--sample", choices=["first", "spread"], default="spread",
                    help="with --limit: 'spread' takes pages evenly from every top folder (default), 'first' the first N")
    ap.add_argument("--include", help="only URLs containing this text")
    ap.add_argument("--exclude", help="skip URLs containing this text")
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--out", help="write every page's row as JSON")
    ap.add_argument("--examples", type=int, default=5)
    args = ap.parse_args()

    urls = list(dict.fromkeys(sitemap_urls(args.sitemap)))
    if args.include:
        urls = [u for u in urls if args.include in u]
    if args.exclude:
        urls = [u for u in urls if args.exclude not in u]
    total = len(urls)
    if args.limit and total > args.limit:
        if args.sample == "first":
            urls = urls[: args.limit]
        else:  # round-robin over top-level folders so every section is represented
            folders = collections.OrderedDict()
            for u in urls:
                folders.setdefault("/".join(urllib.parse.urlsplit(u).path.split("/")[:2]), []).append(u)
            picked, i = [], 0
            while len(picked) < args.limit:
                for group in folders.values():
                    if i < len(group) and len(picked) < args.limit:
                        picked.append(group[i])
                i += 1
            urls = picked
    if not urls:
        sys.exit("no URLs found in the sitemap")
    partial = len(urls) < total
    print(f"auditing {len(urls)} of {total} sitemap pages from {args.sitemap}", file=sys.stderr)

    with cf.ThreadPoolExecutor(args.workers) as pool:
        rows = list(pool.map(analyse, urls))
    by_url = {norm(r["url"]): r for r in rows}

    # Things only visible across pages.
    inlinks = collections.Counter()
    linked_outside_sitemap = collections.Counter()
    for r in rows:
        for target in r.get("links", []):
            if target == norm(r["url"]):
                continue
            if target in by_url:
                inlinks[target] += 1
            elif not re.search(r"\.(png|jpe?g|svg|webp|ico|xml|txt|pdf|json|css|js)$", target):
                linked_outside_sitemap[target] += 1
    for key, r in by_url.items():
        if r["status"] != 200:
            continue
        n = inlinks.get(key, 0)
        r["inlinks"] = n
        if n == 0:
            r["issues"].append("no internal link points here")
        elif n == 1:
            r["issues"].append("only one internal link points here")
        if r.get("title") and r.get("h1") and r["title"].split(" | ")[0].strip() == r["h1"][0]:
            r["issues"].append("title equals h1")
        for code, target in (r.get("hreflang") or {}).items():
            partner = by_url.get(norm(target))
            if partner and partner.get("hreflang") is not None and norm(r["url"]) not in {norm(v) for v in partner["hreflang"].values()}:
                r["issues"].append(f"hreflang partner {code} does not link back")
    for field, label in (("title", "duplicate title"), ("description", "duplicate description")):
        groups = collections.defaultdict(list)
        for r in rows:
            if r.get(field):
                groups[r[field]].append(r)
        for group in groups.values():
            if len(group) > 1:
                for r in group:
                    r["issues"].append(label)

    # Internal links to pages that are not in the sitemap: do they answer?
    broken = []
    all_sitemap = {norm(u) for u in sitemap_urls(args.sitemap)} if partial else set()
    linked_outside_sitemap = collections.Counter({t: n for t, n in linked_outside_sitemap.items() if t not in all_sitemap})
    targets = [t for t, _ in linked_outside_sitemap.most_common(300)]
    with cf.ThreadPoolExecutor(args.workers) as pool:
        for target, (status, final, _, _) in zip(targets, pool.map(fetch, targets)):
            if status != 200:
                broken.append((target, status))
    sources = collections.defaultdict(list)
    for r in rows:
        for target, status in broken:
            if target in r.get("links", []):
                sources[target].append(r["url"])

    counts = collections.Counter(i for r in rows for i in r["issues"])
    print(f"\n# Site audit: {len(rows)} of {total} sitemap pages, {sum(1 for r in rows if not r['issues'])} without findings\n")
    if partial:
        print(f"Sample of {len(rows)} pages ({args.sample}). Internal-link counts and hreflang checks only see links among the "
              "audited pages, so 'no / only one internal link' findings are unreliable; run without --limit to confirm them.\n")
    for issue, n in counts.most_common():
        examples = [r["url"] for r in rows if issue in r["issues"]][: args.examples]
        print(f"## {issue}: {n}")
        for u in examples:
            print(f"  {u}")
    if broken:
        print(f"\n## internal links to pages that do not answer 200: {len(broken)}")
        for target, status in broken[:20]:
            print(f"  {status} {target}  (linked from {sources[target][0] if sources[target] else '?'})")
    broken_set = {t for t, _ in broken}
    missing = [(t, n) for t, n in linked_outside_sitemap.most_common() if t not in broken_set]
    if missing and not partial:
        print(f"\n## linked internally, answer 200, but not in the sitemap: {len(missing)}")
        for target, n in missing[:20]:
            print(f"  {target}  ({n} links)")
    types = collections.Counter(t for r in rows for t in r.get("types", []))
    print("\n## structured data types in use: " + ", ".join(f"{t} {n}" for t, n in types.most_common()))
    langs = collections.Counter(r.get("lang") or "?" for r in rows if r["status"] == 200)
    print("## pages by language: " + ", ".join(f"{l} {n}" for l, n in langs.most_common()))

    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            json.dump({"sitemap": args.sitemap, "pages": rows, "broken_links": broken}, f, ensure_ascii=False, indent=1)
        print(f"\nrows written to {args.out}", file=sys.stderr)


if __name__ == "__main__":
    main()
