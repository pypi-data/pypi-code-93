'''
Template Manager Tool
'''
import click, os, subprocess as sp
import json, templater
from random import randint
tmplt_file = templater.__file__.replace('__init__.py','templates.py')
tmplt=json.load(open(tmplt_file,'r'))

def print_version(ctx, param, value):
    if not value or ctx.resilient_parsing:
        return
    click.echo(f'You are using templater version:{templater.__version__}')
    ctx.exit()
def print_issue(ctx, param, value):
    if not value or ctx.resilient_parsing:
        return
    click.echo(f'post your issue on {templater.issue_track}')
    ctx.exit()

@click.group()
@click.option('--version','-V', is_flag=True, callback=print_version,
              expose_value=False, is_eager=True,help='shows the version of this cli app')
@click.option('--issue','-i',is_flag=True, callback=print_issue,
              expose_value=False, is_eager=True,help='shows github issue tracking url')
def main():
  '''
\t\tTemplate Project Manager\n
It will help you to speed up your workflow.
It loads a basic project structure on a subject.
--sayam(creator)\n
Happy Coding..'''
  pass

_ = main.command

def s(path, dlist:list):
  dct = {}
  for name in dlist:
    if os.path.isfile(path+'/'+name):
      dct[name] = str(open(path+'/'+name,'rb').read())
  return dct
    
    

@_()
@click.argument('template_name', required=True)
@click.argument('path', required=False, type=click.Path(exists=True))
def new(template_name,path='.'):
  ''' For use a folder as template'''
  path = os.path.abspath(path)
  listdir = []
  for path_, dir_, file_ in os.walk(path):
    listdir.append({'path':path_[len(path+'/'):],'dirs':dir_ ,'files': s(path_,file_)})
  tmplt[template_name] = listdir
  json.dump(tmplt, open(tmplt_file,'w'))
  click.secho(f'{path} successfully Init as Template, "{template_name}"',fg='blue')

@_()
def show():
  '''
  shows available templates'''
  click.secho('\n'.join(tmplt.keys()), fg='blue')

@_()
@click.argument('project_name', required=True)
@click.argument('template_name', required=True)
def load(template_name, project_name):
  '''
  Load a template on your Project.
$ tmt load <PROJECT_NAME> <TEMPLATE_NAME>
after load, you will see a folder on current dir as your project name.
  '''
  
  if template_name not in tmplt:
    click.secho(f'''![ERROR]: Not Found Template \"{template_name}\"
    For see available templates use *tpm show*''',fg="red")
    return
  os.mkdir(project_name)
  os.chdir(project_name)
  with click.progressbar(tmplt[template_name], label=f"Setting up {template_name} template") as bar:
    for gg in bar:
        path = gg['path']
        dirs = gg['dirs']
        files=gg['files']
        if dirs != []:
           for _dir in dirs:
             os.mkdir(path+_dir)
        for _filename, content in files.items():
          with open(path+_filename,'wb') as fl:
            fl.write(eval(content))
  click.secho(f"template {template_name} successfully loaded on {project_name} dir")
  

@_()
@click.argument('template_name',required=True)
@click.option('--confirm','-c',type=click.Choice(['yes','no'],case_sensitive=False),
prompt='Confirmation[yes/no]: ')
def remove(template_name,confirm):
  '''For Removing Templates'''
  if confirm == 'no':
    click.echo('Command Canceled')
    return
  template=tmplt.get(template_name)
  if template==None:
    click.secho(f"No '{template_name}' template found",fg='red')
    return
  tmplt.pop(template_name)
  json.dump(tmplt,open(tmplt_file,'w'))
  click.secho(f'{template_name} successfully removed',fg='green')