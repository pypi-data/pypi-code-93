import os
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import webbrowser

import yaml
from jinja2 import Template

from pypandoc.pandoc_download import download_pandoc




def load_config():
    with open("config.yaml") as conf:
        config = yaml.safe_load(conf)
        os.environ.setdefault("PYPANDOC_PANDOC", config["pandoc_bin"])
        return config


def render_titlepage():
    titlepage_md = Path(__file__).parent / "titlepage.md"

    with open("titlepage.yml") as yml:
        variables = yaml.safe_load(yml)
        titlepage_template = Template(titlepage_md.read_text())
        now = datetime.now()
        return titlepage_template.render(**variables, date=f"{now: %d/%m/%Y}")


def load_definitons(path):
    with path.open("r") as yml:
        definitions = yaml.safe_load(yml)
        print(definitions)
        return sorted(
            [Definition(k, v) for k, v in definitions.items()], key=lambda d: d.name
        )


def render_glossary(yml_path, md_path):
    glossary_template = Template(md_path.read_text())
    return glossary_template.render(definitions=load_definitons(yml_path))


if __name__ == "__main__":
    load_config()
    ensure_pandoc()
    md = render_titlepage()
    render_pdf(md, "out.pdf")

    glossary_md = render_glossary(
        Path(__file__).parent / "glossary.yml", Path(__file__).parent / "glossary.md"
    )

    print(glossary_md)

    render_pdf(glossary_md, "glossary.pdf")

    webbrowser.open("glossary.pdf")
