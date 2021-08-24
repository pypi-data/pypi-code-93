import click
from .Generator import Generator

@click.group()
def cli():
    pass

@cli.command('create')
@click.argument('project_name')
def create(project_name):
    '''
    Create the project and all of its directories
    '''
    generator = Generator(project_name)
    generator.create_directories()
    
@cli.command('generate')
@click.argument('project_name')
def generate(project_name):
    '''
    Generate the site from the files in the project directory
    '''
    generator = Generator(project_name)
    # Load the config.json file here
    generator.generate_site()

def cmd():
    cli()