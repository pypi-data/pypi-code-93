from dataclasses import dataclass
from pathlib import Path

from . import pandoc, utils


GLOSSARY_MD_TEMPLATE = Path(__file__).parent / "templates/glossary.md"


@dataclass
class Definition:
    name: str
    value: str


def create_glossary(yml_path):
    return pandoc.render_markdown_template(
        GLOSSARY_MD_TEMPLATE,
        definitions=sorted([
            Definition(k, v) for k, v in utils.read_yml_file(yml_path).items()
            ], key=lambda x: x.name),
    )
