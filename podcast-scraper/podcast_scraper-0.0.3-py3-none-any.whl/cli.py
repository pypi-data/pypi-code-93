import click

from podcast_scraper.france_culture import FranceCulture
from podcast_scraper.monde_diplo import MondeDiplo


@click.group()
def click_france_culture():
    pass


@click_france_culture.command()
@click.option(
    "--url",
    default="https://www.franceculture.fr/emissions/carbone-14-le-magazine-de-larcheologie",
)
def france_culture(url):
    """Get podcast url for France Culture"""
    FranceCulture().print_urls(url)


@click.group()
def click_monde_diplo():
    pass


@click_monde_diplo.command()
@click.option(
    "--url",
    default="https://www.monde-diplomatique.fr/audio?debut_sons=0#pagination_sons",
)
def monde_diplo(url):
    """Get podcast url for Monde Diplo"""
    MondeDiplo().print_urls(url)


cli = click.CommandCollection(sources=[click_france_culture, click_monde_diplo])

if __name__ == "__main__":
    cli()
