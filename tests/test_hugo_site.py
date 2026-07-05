import os
import shutil
import subprocess
import tempfile
import textwrap
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
HUGO = shutil.which("hugo")


def copy_project() -> tempfile.TemporaryDirectory:
    temp_dir = tempfile.TemporaryDirectory()
    dest = Path(temp_dir.name) / "site"

    def ignore(_src, names):
        return {
            name
            for name in names
            if name in {".git", "public", "resources"}
            or name.endswith(".pyc")
            or name == "__pycache__"
        }

    shutil.copytree(REPO_ROOT, dest, ignore=ignore)
    papers_dir = dest / "content" / "papers"
    if papers_dir.exists():
        for paper in papers_dir.glob("*.md"):
            if paper.name != "_index.md":
                paper.unlink()
    return temp_dir


def write_paper(
    site: Path, slug: str, frontmatter: str, body: str | None = None
) -> None:
    paper_dir = site / "content" / "papers"
    paper_dir.mkdir(parents=True, exist_ok=True)
    if body is None:
        body = """
        ## 一言でいうと

        A concise explanation.

        ## 背景

        Background notes.

        ## 手法

        Method notes.

        ## 結果

        Result notes.

        ## 限界

        Limitation notes.

        ## 自分用メモ

        Private reading notes.
        """
    (paper_dir / f"{slug}.md").write_text(
        "---\n"
        + textwrap.dedent(frontmatter).strip()
        + "\n---\n\n"
        + textwrap.dedent(body).strip()
        + "\n",
        encoding="utf-8",
    )


def build_site(site: Path) -> subprocess.CompletedProcess[str]:
    assert HUGO is not None
    return subprocess.run(
        [HUGO, "--destination", "public"],
        cwd=site,
        text=True,
        capture_output=True,
        check=False,
    )


def read_public(site: Path, relative_path: str) -> str:
    return (site / "public" / relative_path).read_text(encoding="utf-8")


@unittest.skipIf(HUGO is None, "hugo is required for site build tests")
class HugoSiteTests(unittest.TestCase):
    def test_empty_papers_page_builds_without_sample_articles(self):
        with copy_project() as temp_dir:
            site = Path(temp_dir) / "site"
            result = build_site(site)

            self.assertEqual(result.returncode, 0, result.stderr)
            papers_index = read_public(site, "papers/index.html")
            self.assertIn("No papers yet", papers_index)
            self.assertNotIn("sample-paper", papers_index.lower())

    def test_detail_page_and_list_render_required_metadata(self):
        with copy_project() as temp_dir:
            site = Path(temp_dir) / "site"
            write_paper(
                site,
                "sample-paper",
                """
                title: "Retrieval-Augmented Generation Survey"
                authors: ["Alice Smith", "Bob Jones"]
                year: 2024
                venue: "ICML"
                paper_url: "https://example.com/rag.pdf"
                tags: ["LLM", "RAG"]
                summary: "Controlled list summary for RAG."
                """,
            )

            result = build_site(site)

            self.assertEqual(result.returncode, 0, result.stderr)
            list_html = read_public(site, "papers/index.html")
            detail_html = read_public(site, "papers/sample-paper/index.html")

            for expected in [
                "Retrieval-Augmented Generation Survey",
                "Controlled list summary for RAG.",
                "Alice Smith",
                "Bob Jones",
                "2024",
                "ICML",
                "https://example.com/rag.pdf",
                "LLM",
                "RAG",
                "/papers/sample-paper/",
            ]:
                self.assertIn(expected, list_html)

            for expected in [
                "Retrieval-Augmented Generation Survey",
                "Alice Smith",
                "Bob Jones",
                "2024",
                "ICML",
                "https://example.com/rag.pdf",
                "LLM",
                "RAG",
                "一言でいうと",
                "背景",
                "手法",
                "結果",
                "限界",
                "自分用メモ",
            ]:
                self.assertIn(expected, detail_html)

    def test_list_uses_frontmatter_summary_not_body_excerpt(self):
        with copy_project() as temp_dir:
            site = Path(temp_dir) / "site"
            write_paper(
                site,
                "summary-contract",
                """
                title: "Summary Contract"
                authors: ["Alice Smith"]
                year: 2023
                venue: "NeurIPS"
                paper_url: "https://example.com/summary.pdf"
                tags: ["LLM"]
                summary: "Only this summary should appear on the list."
                """,
                """
                ## 一言でいうと

                This body opening must not become the list excerpt.
                """,
            )

            result = build_site(site)

            self.assertEqual(result.returncode, 0, result.stderr)
            list_html = read_public(site, "papers/index.html")
            self.assertIn("Only this summary should appear on the list.", list_html)
            self.assertNotIn(
                "This body opening must not become the list excerpt.", list_html
            )

    def test_papers_are_sorted_by_year_descending_then_title(self):
        with copy_project() as temp_dir:
            site = Path(temp_dir) / "site"
            for slug, title, year in [
                ("older", "Older Paper", 2021),
                ("newer", "Newer Paper", 2024),
                ("middle", "Middle Paper", 2022),
                ("same-year-a", "Alpha Same Year", 2024),
            ]:
                write_paper(
                    site,
                    slug,
                    f"""
                    title: "{title}"
                    authors: ["Alice Smith"]
                    year: {year}
                    venue: "ICML"
                    paper_url: "https://example.com/{slug}.pdf"
                    tags: ["LLM"]
                    summary: "Summary for {title}."
                    """,
                )

            result = build_site(site)

            self.assertEqual(result.returncode, 0, result.stderr)
            list_html = read_public(site, "papers/index.html")
            self.assertLess(
                list_html.index("Alpha Same Year"), list_html.index("Newer Paper")
            )
            self.assertLess(
                list_html.index("Newer Paper"), list_html.index("Middle Paper")
            )
            self.assertLess(
                list_html.index("Middle Paper"), list_html.index("Older Paper")
            )

    def test_search_contract_uses_title_and_summary_only(self):
        with copy_project() as temp_dir:
            site = Path(temp_dir) / "site"
            write_paper(
                site,
                "search-contract",
                """
                title: "Transformer Inference"
                authors: ["Retrieval Author"]
                year: 2024
                venue: "RetrievalConf"
                paper_url: "https://example.com/search.pdf"
                tags: ["LLM"]
                summary: "Optimization techniques for serving."
                """,
            )

            result = build_site(site)

            self.assertEqual(result.returncode, 0, result.stderr)
            list_html = read_public(site, "papers/index.html")
            self.assertIn('id="paper-search"', list_html)
            self.assertIn('data-search-title="Transformer Inference"', list_html)
            self.assertIn(
                'data-search-summary="Optimization techniques for serving."',
                list_html,
            )
            self.assertNotIn("data-search-authors", list_html)
            self.assertNotIn("data-search-venue", list_html)

    def test_tag_filter_contract_is_present_on_list_page(self):
        with copy_project() as temp_dir:
            site = Path(temp_dir) / "site"
            write_paper(
                site,
                "rag-paper",
                """
                title: "RAG Paper"
                authors: ["Alice Smith"]
                year: 2024
                venue: "ICML"
                paper_url: "https://example.com/rag.pdf"
                tags: ["LLM", "RAG"]
                summary: "Retrieval summary."
                """,
            )
            write_paper(
                site,
                "vision-paper",
                """
                title: "Vision Paper"
                authors: ["Bob Jones"]
                year: 2023
                venue: "CVPR"
                paper_url: "https://example.com/vision.pdf"
                tags: ["Vision"]
                summary: "Vision summary."
                """,
            )

            result = build_site(site)

            self.assertEqual(result.returncode, 0, result.stderr)
            list_html = read_public(site, "papers/index.html")
            self.assertIn('data-tag-filter="RAG"', list_html)
            self.assertIn('data-tag-filter="Vision"', list_html)
            self.assertIn(
                'data-tags="[&#34;LLM&#34;,&#34;RAG&#34;]"',
                list_html,
            )
            self.assertIn('data-tags="[&#34;Vision&#34;]"', list_html)

    def test_status_frontmatter_is_not_required(self):
        with copy_project() as temp_dir:
            site = Path(temp_dir) / "site"
            write_paper(
                site,
                "no-status",
                """
                title: "No Status Paper"
                authors: ["Alice Smith"]
                year: 2024
                venue: "ICLR"
                paper_url: "https://example.com/no-status.pdf"
                tags: ["LLM"]
                summary: "This article intentionally has no status."
                """,
            )

            result = build_site(site)

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("No Status Paper", read_public(site, "papers/index.html"))
            self.assertIn(
                "No Status Paper", read_public(site, "papers/no-status/index.html")
            )

    def test_github_pages_base_url_and_workflow_are_configured(self):
        config_candidates = [
            REPO_ROOT / "hugo.toml",
            REPO_ROOT / "config.toml",
            REPO_ROOT / "hugo.yaml",
            REPO_ROOT / "config.yaml",
        ]
        config_text = "\n".join(
            path.read_text(encoding="utf-8")
            for path in config_candidates
            if path.exists()
        )
        self.assertIn("https://goropikari.github.io/papers/", config_text)

        workflow_dir = REPO_ROOT / ".github" / "workflows"
        workflow_text = "\n".join(
            path.read_text(encoding="utf-8") for path in workflow_dir.glob("*.yml")
        )
        workflow_text += "\n".join(
            path.read_text(encoding="utf-8") for path in workflow_dir.glob("*.yaml")
        )
        self.assertIn("hugo", workflow_text.lower())
        self.assertIn("actions/upload-pages-artifact", workflow_text)
        self.assertIn("actions/deploy-pages", workflow_text)


if __name__ == "__main__":
    unittest.main()
