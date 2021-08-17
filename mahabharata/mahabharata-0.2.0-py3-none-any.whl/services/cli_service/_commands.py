import click
from mahabharata.services.poet_service.query import get_all_verses_by_author, all_verses


@click.command()
@click.option("--author", "-u", help="Query poem by this author", type=str)
@click.option("--all", "-a", help="list all in scope, overides limit", is_flag=True)
@click.option("--limit", "-l", help="Limit poems to 'N', where 0 < N <= 10", default=1)
@click.option("--collabs", "-c", help="Show collaborators with poem", is_flag=True)
def verses(author: str, all: bool, limit: int, collabs: bool) -> None:
    """Query Mahabharata poems, the default behaviour will give you all verses in list with there authors."""

    def get_quote(iterable, all):
        for index, verse in enumerate(iterable):
            if index == limit and not all:
                return

            click.echo(verse.quote)
            click.echo(f"by: {author or ', '.join(verse.authors).strip(', ')}")
            if collabs and author:
                collaborators = {
                    co_author for co_author in verse.authors if co_author != author
                }
                click.echo(
                    f"collaborator{'s' if len(collaborators) > 1 else ''}: {', '.join(collaborators).strip(', ')}"
                )
            click.echo()

    if not author:
        get_quote(all_verses(), all=(limit == 1))

    else:
        get_quote(get_all_verses_by_author(author=author), all=all)
