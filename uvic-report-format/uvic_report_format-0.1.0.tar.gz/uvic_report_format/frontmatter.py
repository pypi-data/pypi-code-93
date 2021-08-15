from . import pandoc
from pathlib import Path

templates_dir = Path(__file__).parent / "templates"

def create_frontmatter(**kwargs):
    template_path = templates_dir / "frontmatter.md"
    md = pandoc.render_markdown_template(template_path, **kwargs)
    return md
