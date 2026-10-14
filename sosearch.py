#!/usr/bin/env python3
"""360 搜索抓取器 —— 国内尽调检索的主力手段。

为什么用它：企查查/爱企查/职友集/猎聘/看准网都做了反爬（JS 挑战、302、WAF），
但搜索引擎已经把它们的正文片段索引进了结果摘要。所以读 360 的结果摘要，
比硬爬这些站点更省事、更稳定，且拿到的是原文措辞而非二手转述。

用法:
    python3 sosearch.py "英力士 天津 员工"
    python3 sosearch.py "查询词" --num 20
    python3 sosearch.py "查询词" --raw      # 打印原始 HTML 长度，用于排查限流
"""

import argparse
import html
import re
import sys
import urllib.parse
import urllib.request

UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126 Safari/537.36"
)


def fetch(q, num=10):
    url = "https://www.so.com/s?q=" + urllib.parse.quote(q) + f"&rn={num}"
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": UA,
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Accept": "text/html,application/xhtml+xml",
        },
    )
    with urllib.request.urlopen(req, timeout=20) as r:
        return r.read().decode("utf-8", "ignore")


def strip(s):
    s = re.sub(r"<[^>]+>", " ", s)
    return html.unescape(re.sub(r"\s+", " ", s)).strip()


def parse(page):
    page = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", page, flags=re.S | re.I)
    out = []
    pat = r"<h3[^>]*>(.*?)</h3>(.*?)(?=<h3[^>]*>|<div[^>]*id=\"page\")"
    for m in re.finditer(pat, page, flags=re.S):
        title = strip(m.group(1))
        body = strip(m.group(2))
        if title:
            out.append((title, body[:700]))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("query")
    ap.add_argument("--num", type=int, default=10)
    ap.add_argument("--raw", action="store_true", help="打印原始 HTML 长度")
    a = ap.parse_args()

    page = fetch(a.query, a.num)
    if a.raw:
        print(f"[raw {len(page)} bytes]", file=sys.stderr)

    hits = parse(page)
    if not hits:
        print("（无结果 —— 可能被限流，稍后重试或换关键词）")
        return
    for i, (t, b) in enumerate(hits, 1):
        print(f"### {i}. {t}")
        print(b)
        print()


if __name__ == "__main__":
    main()
