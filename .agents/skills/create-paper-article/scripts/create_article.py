#!/usr/bin/env python3
"""Create a UUID-named Hugo paper article for this repository."""

from __future__ import annotations

import argparse
import sys
import uuid
from pathlib import Path


DEFAULT_BODY = """## 一言でいうと

## 背景

## 手法

## 結果

## 限界

## 自分用メモ
"""


def quote_yaml(value: str) -> str:
    escaped = value.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def yaml_list(values: list[str]) -> str:
    if not values:
        return "[]"
    lines = [""] + [f"  - {quote_yaml(value)}" for value in values]
    return "\n".join(lines)


def read_body(args: argparse.Namespace) -> str:
    if args.body_file:
        body = Path(args.body_file).read_text(encoding="utf-8")
    elif not sys.stdin.isatty():
        body = sys.stdin.read()
    else:
        body = DEFAULT_BODY
    body = body.strip()
    return body if body else DEFAULT_BODY.strip()


def parse_csv(values: list[str]) -> list[str]:
    parsed: list[str] = []
    for value in values:
        parsed.extend(part.strip() for part in value.split(",") if part.strip())
    return parsed


def build_article(args: argparse.Namespace, body: str) -> str:
    authors = parse_csv(args.author)
    tags = parse_csv(args.tag)
    year = str(args.year) if args.year is not None else ""
    front_matter = [
        "---",
        f"title: {quote_yaml(args.title or '')}",
        f"authors:{yaml_list(authors)}",
        f"year: {year}",
        f"venue: {quote_yaml(args.venue or '')}",
        f"paper_url: {quote_yaml(args.url)}",
        f"tags:{yaml_list(tags)}",
        f"summary: {quote_yaml(args.summary or '')}",
        "---",
        "",
        body,
        "",
    ]
    return "\n".join(front_matter)


def output_dir(repo_root: Path, raw_output_dir: str) -> Path:
    path = Path(raw_output_dir)
    if not path.is_absolute():
        path = repo_root / path
    return path


def create_file(out_dir: Path, article: str) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    for _ in range(10):
        path = out_dir / f"{uuid.uuid4()}.md"
        if not path.exists():
            path.write_text(article, encoding="utf-8")
            return path
    raise RuntimeError("failed to generate a unique UUID filename")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Create a Hugo paper article with a UUID filename."
    )
    parser.add_argument("--url", required=True, help="Source paper/article URL.")
    parser.add_argument("--title", default="", help="Paper title.")
    parser.add_argument(
        "--author",
        action="append",
        default=[],
        help="Author name. Repeatable or comma-separated.",
    )
    parser.add_argument("--year", type=int, help="Publication year.")
    parser.add_argument("--venue", default="", help="Publication venue.")
    parser.add_argument(
        "--tag",
        action="append",
        default=[],
        help="Tag. Repeatable or comma-separated.",
    )
    parser.add_argument("--summary", default="", help="One-sentence Japanese summary.")
    parser.add_argument("--body-file", help="Markdown body file. Defaults to stdin.")
    parser.add_argument(
        "--output-dir",
        default="content/papers",
        help="Output directory, relative to repo root by default.",
    )
    parser.add_argument("--repo-root", default=".", help="Repository root.")
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()
    article = build_article(args, read_body(args))
    path = create_file(output_dir(repo_root, args.output_dir), article)
    print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
