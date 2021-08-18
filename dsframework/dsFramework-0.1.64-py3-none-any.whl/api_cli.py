import click
import os, shutil
import re
import sys
import platform
import subprocess

isWindows = platform.system() == 'Windows'

__location__ = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__)))

directories = {
    'main': '',
    'pipeline': '',
    'artifacts': '',
    'models': '',
    'vocabs': '',
    'other': '',
    'preprocessor': '',
    'predictables': '',
    'predictors': '',
    'forcers': '',
    'postprocessor': '',
    'schema': '',
    'tester': '',
    'trainer': '',
    'server': '',
}
class AliasedGroup(click.Group):
    def get_command(self, ctx, cmd_name):
        try:
            cmd_name = ALIASES[cmd_name].name
        except KeyError:
            pass
        return super().get_command(ctx, cmd_name)

@click.group(cls=AliasedGroup)
def cli():
    """
    DS framework cli

    ** how to use **

    g = generate

    create project

    dsf-cli g project my-new-project

    dsf-cli generate project my-new-project

    cd my-new-project

    create forcer

    dsf-cli g forcer my-new-forcer

    create predictable

    dsf-cli g predictable my-new-predictable

    run server

    dsf-cli run-server

    create deploy files

    dsf-cli create-deploy-files

    """
# @click.option("--type", prompt="type", help="type of component")
# @click.option("--project_name", prompt="project_name", help="project_name")
# def apis(type, project_name):


@cli.command()
@click.argument('type')
@click.argument('project_name')
def generate(type, project_name):
    """List all cataloged APIs."""
    try:
        f = globals()["generate_%s" % type]
    except Exception as e:
        click.echo('type ' + type + ' not found')
        return
    f(project_name)

@cli.command()
def run_server():
    currentPipelineFolder = os.path.abspath(os.getcwd())
    currentParentFolder = os.path.join(currentPipelineFolder,"..")
    os.environ["PYTHONPATH"] = currentPipelineFolder
    folder = currentPipelineFolder + '/server/main.py'
    subprocess.call('python ' + folder, shell=True)

@cli.command()
def create_deploy_files():
    copy_deploy_files('')

ALIASES = {
    "g": generate
}

def generate_project(project_name):
    # project_name = clean_name(project_name)
    click.echo('project generated ' + project_name)
    create_project(project_name)

def generate_forcer(fileName):
    fileName = clean_name(fileName)
    create_exist_pipeline_file('forcer', fileName)

def generate_predictable(fileName):
    fileName = clean_name(fileName)
    create_exist_pipeline_file('predictable', fileName)

def clean_name(name):
    name = name.replace('-', '_')
    return name

def create_folders(project_name):
    global directories
    directories['main'] = project_name
    if not os.path.exists(directories['main']):
        os.mkdir(directories['main'])

    create_main_folders('config', 'main')
    create_main_folders('pipeline', 'main')
    create_main_folders('artifacts', 'pipeline')
    create_main_folders('models', 'artifacts')
    create_main_folders('vocabs', 'artifacts')
    # create_main_folders('other', 'artifacts')
    create_main_folders('preprocessor', 'pipeline')
    create_main_folders('predictables', 'pipeline')
    create_main_folders('predictors', 'pipeline')
    create_main_folders('forcers', 'pipeline')
    create_main_folders('postprocessor', 'pipeline')
    create_main_folders('schema', 'pipeline')
    create_main_folders('tester', 'main')
    create_main_folders('trainer', 'main')
    create_main_folders('server', 'main')
    create_main_folders('test_scheme', 'server')

def create_project(project_name):
    create_folders(project_name)
    project_name = clean_name(project_name)
    create_pipeline_file(project_name, directories['artifacts'], 'shared_artifacts')
    create_pipeline_file(project_name, directories['preprocessor'], 'preprocess')
    create_pipeline_file(project_name, directories['predictors'], 'predictor')
    create_pipeline_file(project_name, directories['forcers'], 'forcer')
    create_pipeline_file(project_name, directories['postprocessor'], 'postprocess')
    create_pipeline_file(project_name, directories['predictables'], 'predictable')
    create_pipeline_file(project_name, directories['pipeline'], 'pipeline')
    create_pipeline_file(project_name, directories['main'], 'test_pipeline', False)

    create_scheme_file(project_name, directories['schema'], 'inputs')
    create_scheme_file(project_name, directories['schema'], 'outputs')
    create_scheme_file(project_name, directories['test_scheme'], 'test_input', False)
    create_scheme_file(project_name, directories['test_scheme'], 'test_output', False)
    create_scheme_file(project_name, directories['test_scheme'], '__init__', False)

    # create_tester_file(project_name, directories['tester'], 'tester')
    # create_tester_file(project_name, directories['tester'], 'reporter')
    create_server_file(project_name, directories['server'], 'main', False)
    create_server_file(project_name, directories['server'], 'test_server_post', False)
    create_server_file(project_name, directories['server'], 'pool', False)
    create_server_file(project_name, directories['server'], 'token_generator', False)
    create_server_file(project_name, directories['server'], '__init__', False)
    # create_init_file(directories['server'] + '/__init__.py', 'from server.main import app\nfrom server.pool import InstancePool')
    # create_tester_file(project_name, directories['trainer'], 'trainer')
    # create_pipeline_file(project_name, 'labelizer')
    # create_pipeline_file(project_name, 'pipeline')
    #
    create_project_config_json()
    create_project_gitignore()
    create_server_config_json()
    copy_deploy_files(directories['main'])
    # create_dvc_init_file()
    # create_git_init_file()
    change_to_project_dir()
    run_dvc_init()
    run_git_init()
    #
    # create_tester_file(project_name, 'dataset')
    # create_tester_file(project_name, 'reporter')
    # create_tester_file(project_name, 'tester')
    # create_tester_file(project_name, 'tester_server')


def create_main_folders(targetDir, baseDir):
    global directories
    directories[targetDir] = directories[baseDir] + '/' + targetDir
    if not os.path.exists(directories[targetDir]):
        os.mkdir(directories[targetDir])

def create_pipeline_file(project_name, folder, pipelineType, createInitFile=True):
    data = read_template_file(pipelineType)
    replace_in_template_and_create_file(project_name, folder, pipelineType, data, createInitFile)

def create_scheme_file(project_name, folder, pipelineType, createInitFile=True):
    data = read_template_file('scheme/' + pipelineType)
    replace_in_template_and_create_file(project_name, folder, pipelineType, data, createInitFile)

def create_server_file(project_name, folder, pipelineType, createInitFile=True):
    data = read_template_file('tester/server/' + pipelineType)
    replace_in_template_and_create_file(project_name, folder, pipelineType, data, createInitFile)

def create_tester_file(project_name, folder, pipelineType, createInitFile=True):
    data = read_template_file('tester/' + pipelineType)
    replace_in_template_and_create_file(project_name, folder, pipelineType, data, createInitFile)

def create_exist_pipeline_file(type, fileName):
    pipelineType = type + 's'
    folder = 'pipeline/' + pipelineType
    if os.path.exists(folder):
        data = read_template_file(type)
        fileNameNoUnderscore = to_capitalize_no_underscore(fileName)
        className = fileNameNoUnderscore + type.capitalize()
        currentPipelineFolder = os.path.basename(os.getcwd())
        currentDir = folder.replace('/', '.')

        data = data.replace('generatedClass', className)

        new_file = folder + "/" + fileName + ".py"
        current_init_file = folder + "/__init__.py"
        new_init_export = "from " + currentDir + '.' + fileName + " import " + className

        create_file(new_file, data)
        create_init_file(current_init_file, new_init_export)
        inject_to_pipeline(fileName, className, new_init_export)
    else:
        print('please create a project and go to project location first')
    pass


def read_template_file(pipelineType):
    with open(os.path.join(__location__, 'cli/' + pipelineType + '_template.py'), 'r') as file:
        data = file.read()
        return data

def read_file(file_path):
    with open(file_path, 'r') as file:
        data = file.read()
        return data

def write_to_file(file_path, data):
    with open(file_path, 'w') as file:
        file.write(data)
        file.close()

def replace_in_template_and_create_file(project_name, folder, pipelineType, data, createInitFile):
    pipeline_type_no_underscore = to_capitalize_no_underscore(pipelineType)
    project_name_no_underscore = to_capitalize_no_underscore(project_name)
    className = project_name_no_underscore + pipeline_type_no_underscore
    classNameForBaseObject = project_name_no_underscore + pipeline_type_no_underscore
    currentDir = folder.replace('/', '.')
    currentDirNoMainDir = folder.replace(directories['main'] + '/', '').replace('/', '.')
    currentBaseDir = directories['main'].replace('/', '.')
    currentPipelineDir = directories['pipeline'].replace('/', '.')

    data = data.replace('generatedClassName', classNameForBaseObject)
    data = data.replace('generatedClass', className)
    data = data.replace('original_project_name', project_name)
    data = data.replace('generatedProjectName', project_name_no_underscore)
    data = data.replace('generatedDirectory', currentDir)
    data = data.replace('generatedBaseDir', currentBaseDir)
    data = data.replace('generatedPipelineDir', currentPipelineDir)

    new_file = folder + "/" + pipelineType + ".py"
    create_file(new_file, data)

    if createInitFile:
        new_init_file = folder + "/__init__.py"
        new_init_export = "from " + currentDirNoMainDir + '.' + pipelineType + " import " + className
        create_init_file(new_init_file, new_init_export)

def create_predictable_file(fileName):
    pass

def create_file(new_file_path, data):
    if not os.path.exists(new_file_path):
        f = open(new_file_path, "w")
        f.write(data)
        f.close()
def create_init_file(init_path, init_export):
    if not os.path.exists(init_path):
        f = open(init_path, "w")
        f.write(init_export)
        f.close()
    else:
        f = open(init_path, 'r+')
        data = f.read()
        if init_export not in data:
            if len(data) and not data.endswith('\n'):
                f.write('\n')
            f.write(init_export)
            f.close()

def inject_to_pipeline(fileName, className, new_init_export):
    file_path = 'pipeline/pipeline.py'
    if os.path.exists(file_path):
        data = read_file(file_path)
        new_tab_line = '\n'
        data_changed = False
        last_index_of_import = -1
        first_index_of_add_component = -1
        index_of_class = re.search(r'class[^\n]*', data)

        # finding current indent config
        index_of_build_pipeline = re.search(r'def build_pipeline[^\n]*', data)
        index_of_build_preprocessor = re.search(r'self.preprocessor =[^\n]*', data)
        index_of_build_postprocessor = re.search(r'self.postprocessor =[^\n]*', data)
        index_of_build_pipeline_row = re.search(r'.*def build_pipeline[^\n]*', data)
        if index_of_build_pipeline:
            build_pipeline_indent = (index_of_build_pipeline.start() - index_of_build_pipeline_row.start()) * 2
            new_tab_line = new_tab_line.ljust(build_pipeline_indent + 1)

        new_component_line = 'self.' + fileName + ' = ' + className + '()'
        add_component_line = 'self.add_component(self.' + fileName + ')'

        # finding imports and add components indexes
        last_index_of_add_component = -1
        all_from_import = [i.end() for i in re.finditer(r'from[^\n]*', data)]
        all_add_components = [[i.start(), i.end()] for i in re.finditer(r'self.add_component[^\n]*', data)]
        if len(all_from_import):
            last_index_of_import = all_from_import[-1]
        if len(all_add_components):
            first_index_of_add_component = all_add_components[0][0]
            last_index_of_add_component = all_add_components[-1][-1]
        # finding imports and add components indexes


        index_to_add = 0

        # add import to end of imports or to top of file
        if last_index_of_import > -1 and new_init_export not in data:
            s = '\n' + new_init_export
            index_to_add += len(s)
            data = data[:last_index_of_import] + s + data[last_index_of_import:]
            data_changed = True
        elif index_of_class and new_init_export not in data:
            s = new_init_export + '\n\n'
            index_to_add += len(s)
            data = data[:index_of_class.start()] + s + data[index_of_class.start():]
            data_changed = True

        # check if build_pipeline exist but with no components yet
        if first_index_of_add_component == -1 and last_index_of_add_component == -1 and index_of_build_pipeline:
            s = new_tab_line
            current_end = index_of_build_pipeline.end()
            if index_of_build_preprocessor:
                current_end = index_of_build_preprocessor.end()
            if index_of_build_postprocessor:
                current_end = index_of_build_postprocessor.end()
            index = current_end + index_to_add
            index_to_add += len(s)
            data = data[:index] + s + data[index:]
            data_changed = True
            first_index_of_add_component = current_end
            last_index_of_add_component = current_end

        # adding new component line
        if first_index_of_add_component > -1 and new_component_line not in data:
            first_index_of_add_component += index_to_add
            if len(all_add_components):
                new_component_line = new_component_line + new_tab_line
            index_to_add += len(new_component_line)
            data = data[:first_index_of_add_component] + new_component_line + data[first_index_of_add_component:]
            data_changed = True

        #adding add_component line
        if last_index_of_add_component > -1 and add_component_line not in data:
            last_index_of_add_component += index_to_add
            add_component_line = new_tab_line + add_component_line
            index_to_add += len(add_component_line)
            data = data[:last_index_of_add_component] + add_component_line + data[last_index_of_add_component:]
            data_changed = True

        if data_changed:
            write_to_file(file_path, data)

def create_project_config_yaml():
    with open(os.path.join(__location__, 'cli/config.yaml'), 'r') as file:
        data = file.read()
        data = data.replace('generatedDirectory', directories['main'])
        new_file = directories['main'] + '/pipeline/config.yaml'
        if not os.path.exists(new_file):
            f = open(new_file, "w")
            f.write(data)
            f.close()

def create_project_config_json():
    with open(os.path.join(__location__, 'cli/config.json'), 'r') as file:
        data = file.read()
        data = data.replace('generatedDirectory', directories['main'])
        new_file = directories['main'] + '/config/config.json'
        if not os.path.exists(new_file):
            f = open(new_file, "w")
            f.write(data)
            f.close()

def create_project_gitignore():
    with open(os.path.join(__location__, 'cli/.gitignore'), 'r') as file:
        data = file.read()
        new_file = directories['main'] + '/.gitignore'
        if not os.path.exists(new_file):
            f = open(new_file, "w")
            f.write(data)
            f.close()

def create_server_config_json():
    with open(os.path.join(__location__, 'cli/cors_allowed_origins.json'), 'r') as file:
        data = file.read()
        data = data.replace('generatedDirectory', directories['main'])
        new_file = directories['server'] + '/cors_allowed_origins.json'
        if not os.path.exists(new_file):
            f = open(new_file, "w")
            f.write(data)
            f.close()

def change_to_project_dir():
    os.chdir(directories['main'])

def run_dvc_init():
    dir_path = os.getcwd()
    if not os.path.isdir(dir_path + '/.dvc'):
        command = 'dvc_init.sh'
        if not isWindows:
            command = './' + command
        subprocess.call(command, shell=True)

def run_git_init():
    dir_path = os.getcwd()
    if not os.path.isdir(dir_path + '/.git'):
        command = 'git_init.sh'
        if not isWindows:
            command = './' + command
        subprocess.call(command, shell=True)

def copy_deploy_files(main_dir):
    currentPipelineFolder = os.path.basename(os.getcwd())
    if main_dir:
        currentPipelineFolder = main_dir
    dir = os.path.join(__location__, 'cli/tester/deploy_files/')
    listOfFiles = list()
    for (dirpath, dirname, filenames) in os.walk(dir):
        dirpath = dirpath.replace(dir, '')
        listOfFiles += [os.path.join(dirpath, file) for file in filenames]
        for file_path in listOfFiles:
            with open(os.path.join(dir, file_path), 'r', encoding="utf8") as file:
                try:
                    data = file.read()
                    data = data.replace('{name-your-service}', currentPipelineFolder)
                    data = data.replace('{name-your-artifacts}', currentPipelineFolder)
                    dirToCreate = ''
                    if main_dir:
                        dirToCreate = main_dir + '/'
                    if not os.path.exists(dirToCreate + 'deploy'):
                        os.makedirs(dirToCreate + 'deploy')
                    if not os.path.exists(dirToCreate + file_path):
                        f = open(dirToCreate + file_path, "w")
                        f.write(data)
                        f.close()
                        # Make sure that .sh files can be executed
                        if (dirToCreate + file_path).endswith('.sh'):
                            os.chmod(dirToCreate + file_path, 0o744)
                except Exception as ex:
                    pass
    # for item in os.listdir(dir):
    #     s = os.path.join(dir, item)
    #     d = os.path.join(main_dir, item)
    #     if os.path.isdir(s):
    #         shutil.copytree(s, d, False, None)
    #     else:
    #         shutil.copy2(s, d)

def to_capitalize_no_underscore(text):
    return ''.join(elem.capitalize() for elem in text.split('_'))

if __name__ == '__main__':
    cli(prog_name='cli')
