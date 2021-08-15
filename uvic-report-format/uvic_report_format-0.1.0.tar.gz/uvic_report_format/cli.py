import webbrowser
from pathlib import Path

import click

from .models import Report
from . import frontmatter, glossary, pandoc

coverpage = Path(__file__).parent/"templates/titlepage.md"

@click.group()
def cli():
    ...


@click.option(
    "--yml-file",
    "-f",
    default="./config.yml",
    help="The YAML config file.",
    type=click.Path(),
)
@click.option(
    "-o", "--open",
    is_flag=True,
)
@cli.command()
def compile(yml_file, open):
    report = Report.parse_file(yml_file)

    titlepage_md = frontmatter.create_frontmatter(
        **report.info.dict()
    )

    glossary_md = glossary.create_glossary(report.content.glossary)

    include_before = [
        coverpage.read_text(),
        report.content.personal_reflection.read_text(),
        report.content.executive_summary.read_text(),
    ]

    content = [
        titlepage_md,
        glossary_md,
        report.content.introduction.read_text(),
        (
            r"\renewcommand{\thesection}{\arabic{section}}"
            "\n"
            r"\renewcommand{\thesubsection}{\arabic{subsection}}"
            "\n"
            r"\setcounter{section}{0}"
            "\n"
            r"\setcounter{page}{0}"
            "\n"
            r"\pagenumbering{arabic}"
        ),
        report.content.body.read_text(),
        r"\renewcommand{\thesection}{}" + "\n",
        report.content.conclusion.read_text(),
    ]

    report_pdf = pandoc.multiple_md_to_pdf(
        report.config.output,
        *content,
        include_before="\n".join(include_before)
    )

    if open:
        webbrowser.open(str(report_pdf))