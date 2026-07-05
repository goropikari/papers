---
name: create-paper-article
description: Create a Japanese Hugo paper note from a URL and save it as a UUID-named Markdown file in this repository. Use when the user provides a paper/article URL and asks to add, create, summarize, or write an article/note for the Papers site, especially when the filename must be generated as a UUID.
---

# Create Paper Article

## Overview

Create one Markdown file under `content/papers/` from a source URL. Use the bundled script to enforce UUID filenames and the repository's front matter shape.

## Workflow

1. Fetch and inspect the URL content. If the environment cannot access the URL, ask for the source text or PDF content rather than inventing details.
2. Extract bibliographic metadata when available: title, authors, year, venue, source URL, tags, and a one-sentence Japanese summary.
3. Write the article body in Japanese using this repository's sections:
   - `## 一言でいうと`
   - `## 背景`
   - `## 手法`
   - `## 結果`
   - `## 限界`
   - `## 自分用メモ`
4. Run `scripts/create_article.py` from this skill to create the file. Prefer piping the final body through stdin so the script owns front matter and UUID filename generation.
5. Report the created path and mention any metadata that could not be verified.

## Script Usage

Run from the repository root:

```bash
python3 .agents/skills/create-paper-article/scripts/create_article.py \
  --url "https://example.com/paper" \
  --title "Paper Title" \
  --author "First Author" \
  --author "Second Author" \
  --year 2026 \
  --venue "arXiv" \
  --tag "LLM" \
  --tag "Evaluation" \
  --summary "日本語の短い要約。" < /tmp/article-body.md
```

The script prints the created Markdown path. It refuses to overwrite files and always uses a new UUID v4 filename.

## Article Rules

- Do not use a slug or source title for the filename.
- Keep front matter compatible with `archetypes/papers.md`.
- Leave unknown scalar metadata empty, except `paper_url`, which must be the provided URL.
- Use concise tags in Title Case or the style already present in this repository.
- Do not include unsupported claims. Mark uncertainty in prose when the source is ambiguous.
