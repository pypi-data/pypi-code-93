from ..ns_util import ns, ns_path
from pathlib import Path
from datetime import datetime as dt
from staticjinja import Site
from functools import partial
import markdown

__all__ = ["standup"]

markdowner = markdown.Markdown(output_format="html5")

def standup(domains_list=None, verbose=True):
    domains_list = domains_list or [*ns]
    for domain in domains_list:
        ns_p = ns_path / domain
        if not ns_p.exists() and ns_p.is_dir():
            raise ValueError(f"{ns_p} not found")
        template_dir = ns_p / "templates"
        if template_dir.exists():
            site_dir = ns_p / "site"
            article_dir = ns_p / "posts"
            extra_ctxs = []
            if article_dir.exists():
                for a in article_dir.iterdir():
                    print(a)
                post_ctxs = [
                    (a.name, article)
                    for a in article_dir.iterdir()
                ]
                cut_templates(article_dir, site_dir, contexts=post_ctxs)
                extra_ctxs.extend([
                    ("index.html", partial(indexed_articles, article_dir=article_dir))
                ])
            cut_templates(template_dir, site_dir, contexts=extra_ctxs)
            print(f"Built {template_dir}")

def fmt_mtime(path_to_file):
    mtime = path_to_file.stat().st_mtime
    date = dt.fromtimestamp(mtime)
    return date.strftime("%Y-%m-%dT%H:%M:%SZ")

def base(template):
    template_path = Path(template.filename)
    return {
        "template_date": fmt_mtime(template_path),
    }

def index(template):
    return {}

def indexed_articles(template, article_dir):
    return {
        "articles": [
            article(a, is_path=True)
            for a in article_dir.iterdir()
            if not a.is_dir() # not sub-directory
            if not a.name.startswith("_") # not partial template
        ]
    }

def article(template, is_path=False):
    template_path = template if is_path else Path(template.filename)
    return {
        "url": template_path.stem, "title": template_path.stem,
        "mtime": fmt_mtime(template_path), "short_desc": "foo bar baz",
    }

def md_context(template):
    markdown_content = Path(template.filename).read_text()
    return {"post_content_html": markdowner.convert(markdown_content)}

def render_md(site, template, **kwargs):
    # i.e. posts/post1.md -> build/posts/post1.html
    out = site.outpath / Path(template.name).with_suffix(".html")
    # Compile and stream the result
    site.get_template("layouts/_post.html").stream(**kwargs).dump(str(out), encoding="utf-8")

def cut_templates(template_dir, out_dir, contexts=None, mergecontexts=True):
    default_ctxs = [(r".*\.(html|md)$", base), ("index.html", index), (r".*\.md", md_context)]
    custom_contexts = contexts or []
    contexts = default_ctxs + custom_contexts
    site = Site.make_site(
        contexts=contexts, mergecontexts=mergecontexts,
        searchpath=template_dir, outpath=out_dir,
        rules=[(r".*\.md", render_md)],
    )
    site.render()
