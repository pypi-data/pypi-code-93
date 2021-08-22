import click
import os
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
    if _check_project_exists(project_name):
        generator = Generator(project_name)
        # Load the config.json file here
        generator.generate_site()
    else:
        print(f'Project \"{project_name}\" does not exist in this directory, '
              f'create it with \"bassg create {project_name}\"')
    
    
def _check_project_exists(project_name):
    '''
    Check that there's a project in the current directory
    '''
    folder_reqs = ['build', 'build\\assets', 'build\\config',
                   'build\\markdown', 'build\\templates', 'site']
    cwd = os.getcwd()
    dirs = os.listdir(cwd)
    
    if project_name in dirs:
        cwd = os.path.join(cwd, project_name)
        os.chdir(cwd)
        roots = []
        for root, dirs, files in os.walk(cwd):
            roots.append(root)
        for folder_req in folder_reqs:
            if os.path.join(cwd, folder_req) not in roots:
                return False
    else:
        return False
                
    os.chdir('..')
    return True
    

if __name__ == '__main__':
    cli()