import os
import tempfile
from shutil import which
from pathlib import Path
from . import utils

from pypandoc import convert_text
from jinja2 import Template
from PyPDF2 import PdfFileMerger


def ensure_pandoc():
    if which("pandoc") is None:
        raise RuntimeError(
            "Pandoc not installed. please install pandoc.\nhttps://pandoc.org/installing.html"
        )


def md_to_pdf(md, outputfile, options=()):
    convert_text(md, "pdf", outputfile=outputfile, format="md", extra_args=options)
    return outputfile


def multiple_md_to_pdf(out, *md, include_before=None):
    lines = []
    for text in md:
        lines.extend(text.split("\n"))
        lines.append("\pagebreak\n")
    full_text = "\n".join(lines)

    build_path = Path(tempfile.mkdtemp())

    options = []
    if include_before is not None:
        outputfile = build_path / "frontmatter.tex"
        outputfile.write_text(include_before)
        convert_text(
            include_before, "tex", format="md", outputfile=str(outputfile),
        )
        options.append(f"--include-before-body={outputfile.absolute()}")

    return md_to_pdf(full_text, str(out), options=options)


def render_markdown_template(
    md_path: os.PathLike, yml_path: os.PathLike = None, **kwargs
):
    vars_ = utils.read_yml_file(yml_path) if yml_path else kwargs
    template = Template(md_path.read_text())
    return template.render(**vars_)


def merge_pdfs(*paths):
    merger = PdfFileMerger()

    for path in paths:
        merger.append(path.open("rb"))

    build_path = config.build_path / "out.pdf"

    with build_path.open("wb") as f:
        merger.write(f)

    return build_path
