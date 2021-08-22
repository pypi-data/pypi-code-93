import os
from glob import glob
from jinja2 import Environment, FileSystemLoader
from distutils.dir_util import copy_tree
from markdown import markdown
from bs4 import BeautifulSoup as bs
from json import load

class Generator:
    def __init__(self, project_name):
        self.__PROJECT_NAME = project_name
        self.__CURRENT_DIR = os.getcwd()
        
        self.__FOLDER_DEFAULTS = {
            'root_folder': f'{self.__CURRENT_DIR}\\{self.__PROJECT_NAME}',
            'build_folder': f'{self.__CURRENT_DIR}\\{self.__PROJECT_NAME}\\build',
            'templates_folder': f'{self.__CURRENT_DIR}\\{self.__PROJECT_NAME}\\build\\templates',
            'assets_folder': f'{self.__CURRENT_DIR}\\{self.__PROJECT_NAME}\\build\\assets',
            'markdown_folder': f'{self.__CURRENT_DIR}\\{self.__PROJECT_NAME}\\build\\markdown',
            'config_folder': f'{self.__CURRENT_DIR}\\{self.__PROJECT_NAME}\\build\\config',
            'output_folder': f'{self.__CURRENT_DIR}\\{self.__PROJECT_NAME}\\site',
        }
        
        self.__MARKDOWN_DEFAULTS = {
            'build_folder': '# This is the build directory, put your HTML files in here',
            'templates_folder': '# This is the templates directory, put your Jinja2 templates in here',
            'assets_folder': '# This is the assets folder, put your assets (images, CSS, etc.) in here',
            'markdown_folder': '# This the markdown folder, put your .md files in here',
            'config_folder': '# This is the config folder, put your json files in here',
        }
        
    def create_directories(self):
        for folder in self.__FOLDER_DEFAULTS:
            os.makedirs(self.__FOLDER_DEFAULTS[folder], exist_ok=True)
            if folder in self.__MARKDOWN_DEFAULTS:
                with open(self.__FOLDER_DEFAULTS[folder] + '\\README.md', mode='w') as file:
                    file.write(self.__MARKDOWN_DEFAULTS[folder])
        print(f'PROJECT CREATED: {self.__PROJECT_NAME}')
    
    def generate_site(self, 
                      beautify=True, 
                      individual_folders=True, 
                      copy_assets=True,
                      ignore_files=None):
        
        build_files = glob(self.__FOLDER_DEFAULTS['build_folder'] + '\\*.html')
        
        if ignore_files:
            for file in ignore_files:
                file = os.path.join(self.__FOLDER_DEFAULTS['build_folder'], file)
                if file in build_files:
                    build_files.remove(file)
                    
        file_loader = FileSystemLoader(self.__FOLDER_DEFAULTS['build_folder'])
        env = Environment(loader=file_loader)
        
        for build_file in build_files:
            filename = build_file.split('\\')[-1] # just the <filename>.html
            template = env.get_template(filename)

            # Check and apply the "folder_struct" json option to the file
            folder_struct = None
            config_data = None
            if self.__get_config(build_file):
                try:
                    folder_struct = self.__get_config(build_file)['folder_struct']
                except:
                    pass
                config_data = self.__get_config(build_file)
            
            if folder_struct:
                os.makedirs(os.path.join(self.__FOLDER_DEFAULTS['output_folder'],  folder_struct), exist_ok=True)
                new_file = os.path.join(folder_struct, filename)
                create_file = os.path.join(self.__FOLDER_DEFAULTS['output_folder'], new_file)
            else:
                create_file = os.path.join(self.__FOLDER_DEFAULTS['output_folder'], filename)
            
            rendered_template = template.render(markdown=self.__get_markdown(build_file), data=config_data)
            
            if beautify:
                soup = bs(rendered_template, features='html.parser')
                rendered_template = soup.prettify()
                # Beautify only adds 1 space by default, add an additional
                # for 2 space tabs
                new_temp = ''
                for line in rendered_template.split('\n'):
                    space_count = 0
                    for char in line:
                        if char != ' ':
                            break
                        space_count += 1
                    spacing = ''
                    for i in range(space_count):
                        spacing += ' '
                    line = spacing + line
                    new_temp += line + '\n'
                new_temp = new_temp[:-1]
                rendered_template = new_temp
            
            with open(create_file, mode='w') as file:
                file.write(rendered_template)
                
        if copy_assets:
            copy_tree(self.__FOLDER_DEFAULTS['assets_folder'], 
                      self.__FOLDER_DEFAULTS['output_folder'] + '\\assets\\')

                                
    def __get_markdown(self, filename):
        filename = filename.split('\\')[-1].split('.')[0]
        files = glob(self.__FOLDER_DEFAULTS['markdown_folder'] + '\\' + filename + '*.md')
        markdown_html = []
        if len(files) > 0:
            for md_file in files:
                with open(md_file, mode='r') as file:
                    raw_markdown = file.read()
                    markdown_html.append(markdown(raw_markdown))
            if len(markdown_html) == 1:
                return markdown_html[0]
            else:
                return markdown_html
        else:
            return None
        
    def __get_config(self, filename):
        filename = filename.split('\\')[-1].split('.')[0]
        configFile = glob(self.__FOLDER_DEFAULTS['config_folder'] + '\\' + filename + '*.json')
        if configFile == []:
            return None
        if len(configFile) > 0:
            configFile = configFile[0]
            
        with open(configFile, mode='r') as file:
            return load(file)
        