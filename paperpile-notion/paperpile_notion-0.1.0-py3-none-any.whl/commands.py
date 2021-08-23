import traceback
from typing import Dict

import click
from click import Context

from tqdm import tqdm
import numpy as np
import pandas as pd
from ruamel.yaml import YAML

from notion.client import NotionClient
from notion.collection import CollectionRowBlock
from notion.block import CollectionViewPageBlock


from paperpile_notion.preprocessing import (
    extract_status,
    extract_fields_methods,
)
from paperpile_notion import crud as CRUD


@click.group(invoke_without_command=True)
@click.help_option("-h", "--help")
@click.option("-t", "--token", "token", help="Your Notion API token.", envvar=["NOTION_TOKEN_V2", "TOKEN"])
@click.pass_context
def cli(ctx: Context, token: str) -> None:
    client_kwargs = {}
    if not token:
        client_kwargs["email"] = click.prompt("Your Notion email addresss")
        client_kwargs["password"] = click.prompt("Your Notion password", hide_input=True)
    else:
        client_kwargs["token_v2"] = token
    # TODO support integration tokens, BLOCK NotionClient doesn't support them
    ctx.obj = {}
    ctx.obj["notion"] = NotionClient(**client_kwargs)
    ctx.obj["config"] = YAML().load(open("config.yml", "r"))


@cli.command()
@click.option("-r", "--refs", "references", required=True)
@click.pass_context
def update_db(ctx: click.Context, references: str) -> None:
    pass


@cli.command()
@click.option("-r", "--refs", "references", required=True)
@click.pass_context
def update_article_db(ctx: click.Context, references: str) -> None:
    notion = ctx.obj["notion"]
    config = ctx.obj["config"]

    assert "articles" in config["blocks"]
    articleCV = notion.get_block(config["blocks"]["articles"]).collection
    authorCV = None
    if "authors" in config["blocks"]:
        authorCV = notion.get_block(config["blocks"]["authors"]).collection

    assert references.endswith(".json")
    df = pd.read_json(references)[[
        "_id", "title", "author", "abstract",
        "labelsNamed", "foldersNamed",
        "journalfull", "journal", "kind",
    ]]

    df[["fields", "methods"]] = pd.DataFrame(df["labelsNamed"].apply(
        extract_fields_methods, config=config["fields-methods"]
    ).tolist())

    status_col = config["status"].get("col" , "foldersNamed")
    df["status"] = df[status_col].apply(extract_status, config=config["status"])
    df["author"] = df["author"].apply(lambda x: x if type(x) == list else [])

    print(f"Found {len(df)} papers in {references} and {len(articleCV.get_rows())}")

    pbar = tqdm(desc="Updating/Creating Articles", total=len(df))
    for idx, row in df.iterrows():
        try:
            entry = CRUD.article(row, articleCV, authorCV)
        except Exception as e:
            tqdm.write(row.title)
            # tqdm.write(str(traceback.format_exc()))
            tqdm.write(str(e))
            import pdb; pdb.set_trace()
        finally:
            pbar.update(1)



@cli.command()
@click.option("-r", "--refs", "references", required=True)
@click.pass_context
def update_author_db(ctx: click.Context, references: str) -> None:
    notion = ctx.obj["notion"]
    config = ctx.obj["config"]

    if not config["authors"]["rollup"]:
        return

    assert "authors" in config["blocks"]
    authorCV = notion.get_block(config["blocks"]["authors"]).collection

    assert references.endswith(".json")
    df = pd.read_json(references)["author"]
    df = pd.melt(df.apply(pd.Series), value_name="author").dropna()["author"]
    df = pd.DataFrame(df.tolist())
    # df["orcid"] = pd.fillna(df["orcid"], "")

    pbar = tqdm(desc="Updating/Creating Authors", total=len(df))
    for idx, row in df.iterrows():
        try:
            entry = CRUD.author(row, authorCV)
        except Exception as e:
            tqdm.write(row.title)
            tqdm.write(str(traceback.format_exc()))
            tqdm.write(str(e))
        finally:
            pbar.update(1)
