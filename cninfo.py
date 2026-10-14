#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""巨潮资讯（cninfo）免费接口客户端 —— 上市公司主体检索 + 公告全文检索。

接口无需认证、无需 key（2026-10 实测可用）：
  POST /new/information/topSearch/query          公司检索（关键词 -> 代码 / orgId）
  POST /new/hisAnnouncement/query                公告检索（支持 stock 精确限定公司）
  GET  http://static.cninfo.com.cn/<adjunctUrl>  公告 PDF 原文

用法：
  python3 cninfo.py search 宁德时代
  python3 cninfo.py ann --code 002594 --size 5
  python3 cninfo.py ann 回购 --code 002594 --since 2026-01-01
  python3 cninfo.py ann "诉讼" --since 2026-01-01 --pages 2 --json
  python3 cninfo.py fetch finalpage/2026-10-08/1225595406.PDF -o /tmp/a.pdf
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone

BASE = "http://www.cninfo.com.cn"
STATIC = "http://static.cninfo.com.cn"
UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
)
CST = timezone(timedelta(hours=8))
TAG = re.compile(r"<[^>]+>")


def _post(path: str, fields: dict) -> object:
    body = urllib.parse.urlencode(fields).encode()
    req = urllib.request.Request(
        BASE + path,
        data=body,
        headers={
            "User-Agent": UA,
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Referer": BASE + "/new/commonUrl?url=disclosure/list/notice",
            "X-Requested-With": "XMLHttpRequest",
        },
    )
    with urllib.request.urlopen(req, timeout=25) as resp:
        payload = resp.read().decode("utf-8", "replace")
    return json.loads(payload)


def search(keyword: str, limit: int = 10) -> list[dict]:
    """关键词 -> 证券代码 / orgId。支持 A 股、港股、新三板、债券。"""
    rows = _post("/new/information/topSearch/query", {"keyWord": keyword, "maxNum": limit})
    return rows or []


def _column_for(code: str) -> str:
    if len(code) == 5 and code.isdigit():
        return "hke"
    if code.startswith("6"):
        return "sse"
    if code.startswith(("0", "3")):
        return "szse"
    if code.startswith(("4", "8")):
        return "third"
    return "szse"


def resolve_stock(code: str) -> tuple[str, str]:
    """把证券代码解析成 cninfo 的 stock 参数值 (code,orgId)，并返回推荐 column。"""
    rows = search(code, limit=10)
    for row in rows:
        if row.get("code") == code:
            return f"{row['code']},{row['orgId']}", _column_for(code)
    if rows:
        top = rows[0]
        return f"{top['code']},{top['orgId']}", _column_for(top["code"])
    raise SystemExit(f"无法解析证券代码：{code}")


def announcements(
    keyword: str = "",
    stock: str | None = None,
    column: str = "szse",
    page: int = 1,
    size: int = 30,
    since: str | None = None,
    until: str | None = None,
) -> dict:
    """公告检索。stock 为 'code,orgId' 时精确限定公司；keyword 为全文检索词。"""
    se_date = f"{since or ''}~{until or ''}" if (since or until) else ""
    res = _post(
        "/new/hisAnnouncement/query",
        {
            "pageNum": page,
            "pageSize": size,
            "column": column,
            "tabName": "fulltext",
            "stock": stock or "",
            "searchkey": keyword or "",
            "seDate": se_date,
            "sortName": "",
            "sortType": "",
            "isHLtitle": "true",
        },
    )
    return res or {}


def _clean(text: str | None) -> str:
    return TAG.sub("", text or "").strip()


def _date(ms: int | None) -> str:
    if not ms:
        return ""
    return datetime.fromtimestamp(ms / 1000, CST).strftime("%Y-%m-%d")


def _in_range(item: dict, since: str | None, until: str | None) -> bool:
    """本地日期过滤。服务端 seDate 与 stock 组合会返回空，故 stock 场景改在本地筛。"""
    day = _date(item.get("announcementTime"))
    if not day:
        return False
    if since and day < since:
        return False
    if until and day > until:
        return False
    return True


def _normalize_range(since: str | None, until: str | None) -> tuple[str | None, str | None]:
    """服务端只认完整区间（'2025-01-01~' 这类半开写法返回空），这里补齐两端。"""
    if not since and not until:
        return None, None
    today = datetime.now(CST).strftime("%Y-%m-%d")
    return since or "1990-01-01", until or today


def cmd_search(args: argparse.Namespace) -> int:
    rows = search(args.keyword, args.limit)
    if args.json:
        print(json.dumps(rows, ensure_ascii=False, indent=2))
        return 0 if rows else 1
    if not rows:
        print(f"未找到匹配「{args.keyword}」的上市主体", file=sys.stderr)
        return 1
    print(f"{'代码':<8}{'简称':<18}{'类别':<8}{'类型':<8}{'orgId':<16}")
    for r in rows:
        print(
            f"{r.get('code', ''):<8}{_clean(r.get('zwjc')):<18}"
            f"{r.get('category', ''):<8}{r.get('type', ''):<8}{r.get('orgId', ''):<16}"
        )
    return 0


def cmd_ann(args: argparse.Namespace) -> int:
    stock = None
    column = args.column
    if args.code:
        stock, auto_column = resolve_stock(args.code)
        if not column:
            column = auto_column
    column = column or "szse"

    # 实测：stock 与 seDate 同时下发时服务端返回空结果，故 stock 场景改为本地过滤日期。
    since, until = _normalize_range(args.since, args.until)
    server_since = None if stock else since
    server_until = None if stock else until

    collected: list[dict] = []
    total = None
    for page in range(1, args.pages + 1):
        res = announcements(
            args.query or "", stock=stock, column=column, page=page, size=args.size,
            since=server_since, until=server_until,
        )
        if total is None:
            total = res.get("totalAnnouncement") or res.get("totalRecordNum") or 0
        batch = res.get("announcements") or []
        if not batch:
            break
        collected.extend(batch)

    if stock and (since or until):
        collected = [a for a in collected if _in_range(a, since, until)]

    if args.json:
        print(json.dumps({"total": total, "items": collected}, ensure_ascii=False, indent=2))
        return 0 if collected else 1

    if not collected:
        print(f"未检索到公告：code={args.code or '-'} query={args.query or '-'}", file=sys.stderr)
        return 1

    scope = f"{args.code} " if args.code else ""
    print(f"命中 {total} 条，展示 {len(collected)} 条  ({scope}column={column})")
    for a in collected:
        url = STATIC + "/" + (a.get("adjunctUrl") or "")
        title = _clean(a.get("announcementTitle"))
        print(
            f"{_date(a.get('announcementTime'))}  "
            f"{a.get('secCode', ''):<8}{_clean(a.get('secName')):<14}{title}\n"
            f"{'':>12}{url}"
        )
    return 0


def cmd_fetch(args: argparse.Namespace) -> int:
    url = args.adjunct if args.adjunct.startswith("http") else STATIC + "/" + args.adjunct.lstrip("/")
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Referer": BASE + "/"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        blob = resp.read()
    out = args.out or url.rsplit("/", 1)[-1]
    with open(out, "wb") as fh:
        fh.write(blob)
    print(f"{len(blob)} bytes -> {out}")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="巨潮资讯免费接口客户端（上市公司尽调）")
    sub = ap.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("search", help="按关键词检索上市主体")
    s.add_argument("keyword")
    s.add_argument("--limit", type=int, default=10)
    s.add_argument("--json", action="store_true")
    s.set_defaults(func=cmd_search)

    a = sub.add_parser("ann", help="公告检索（可精确限定公司）")
    a.add_argument("query", nargs="?", default="", help="全文检索词，可省略")
    a.add_argument("--code", help="证券代码，如 002594 / 300750 / 00700")
    a.add_argument("--column", help="szse/sse/third/hke，默认按代码推断")
    a.add_argument("--since", help="起始日期 YYYY-MM-DD")
    a.add_argument("--until", help="结束日期 YYYY-MM-DD")
    a.add_argument("--pages", type=int, default=1)
    a.add_argument("--size", type=int, default=30)
    a.add_argument("--json", action="store_true")
    a.set_defaults(func=cmd_ann)

    f = sub.add_parser("fetch", help="下载公告 PDF")
    f.add_argument("adjunct", help="adjunctUrl 或完整 URL")
    f.add_argument("-o", "--out")
    f.set_defaults(func=cmd_fetch)

    args = ap.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
