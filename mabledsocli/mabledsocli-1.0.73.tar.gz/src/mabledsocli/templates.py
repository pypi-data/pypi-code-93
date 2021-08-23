
import os
import re
import jinja2
from jinja2 import meta
from .constants import *
from .config import Configs
from .providers import StoreProvider, Providers
from .parameters import Parameters
from .secrets import Secrets
from .logger import Logger
from .dict_utils import merge_dicts, deflatten_dict
from .exceptions import DSOException
from .stages import Stages


REGEX_PATTERN = r"^[a-zA-Z][./a-zA-Z0-9_-]*[a-zA-Z0-9]$"

class TemplateProvider(StoreProvider):
    def list(self, project, application, stage, uninherited=False, include_contents=False, filter=None):
        raise NotImplementedError()
    def add(self, project, application, stage, key, contents, render_path):
        raise NotImplementedError()
    def get(self, project, application, stage, key, revision=None):
        raise NotImplementedError()
    def history(self, project, application, stage, key, include_contents=False):
        raise NotImplementedError()
    def delete(self, project, application, stage, key):
        raise NotImplementedError()


class TemplateManager():

    @property
    def default_render_path(self):
        return Configs.working_dir

    def validate_key(self, key):
        Logger.info(f"Validating template key '{key}'...")
        if not key:
            raise DSOException(MESSAGES['KeyNull'])
        if key == 'dso' or key.startswith('dso.'):
            raise DSOException(MESSAGES['DSOReserverdKey'].format(key))
        if not re.match(REGEX_PATTERN, key):
            raise DSOException(MESSAGES['InvalidKeyPattern'].format(key, REGEX_PATTERN))
        ### the regex does not check adjacent special chars
        if '..' in key:
            raise DSOException(MESSAGES['InvalidKeyStr'].format(key, '..'))

        if '//' in key:
            raise DSOException(MESSAGES['InvalidKeyStr'].format(key, '//'))

    def get_template_render_path(self, key):
        result = Configs.get_template_render_paths(key)
        if result:
            return result[key]

        return f'.{os.sep}' + os.path.relpath(os.path.join(Templates.default_render_path, key), Configs.working_dir) 

    def list(self, stage, uninherited=False, include_contents=False, filter=None):
        project = Configs.project
        application = Configs.application
        stage = Stages.normalize(stage)
        provider = Providers.TemplateProvider()
        Logger.info(f"Start listing templates: project={project}, application={application}, stage={Stages.shorten(stage)}")
        response = provider.list(project, application, stage, uninherited, include_contents, filter)
        for template in response['Templates']:
            key = template['Key']
            template['RenderTo'] = self.get_template_render_path(key)
        
        return response

    def add(self, stage, key, contents, render_path):
        self.validate_key(key)
        project = Configs.project
        application = Configs.application
        stage = Stages.normalize(stage)
        provider = Providers.TemplateProvider()
        Logger.info(f"Start adding template '{key}': project={project}, application={application}, stage={Stages.shorten(stage)}")
        Logger.debug(f"Template: key={key}, render_path={render_path}")
        result = provider.add(project, application, stage, key, contents)
        result['RenderTo'] = render_path
        if os.path.abspath(render_path) == os.path.abspath(os.path.join(self.default_render_path, key)):
            Configs.unregister_template_custom_render_path(key)
        else:
            Configs.register_template_custom_render_path(key, render_path)
        return result

    def get(self, stage, key, revision=None):
        # self.validate_key(key)
        project = Configs.project
        application = Configs.application
        stage = Stages.normalize(stage)
        provider = Providers.TemplateProvider()
        Logger.info(f"Start getting the contents of template '{key}': project={project}, application={application}, stage={Stages.shorten(stage)}")
        result = provider.get(project, application, stage, key, revision)
        result['RenderTo'] = self.get_template_render_path(key)
        return result

    def history(self, stage, key, include_contents=False):
        # self.validate_key(key)
        project = Configs.project
        application = Configs.application
        stage = Stages.normalize(stage)
        provider = Providers.TemplateProvider()
        Logger.info(f"Start getting the history of template '{key}': project={project}, application={application}, stage={Stages.shorten(stage)}")
        return provider.history(project, application, stage, key, include_contents)

    def delete(self, stage, key):
        # self.validate_key(key)
        project = Configs.project
        application = Configs.application
        stage = Stages.normalize(stage)
        provider = Providers.TemplateProvider()
        Logger.info(f"Start deleting template '{key}': project={project}, application={application}, stage={Stages.shorten(stage)}")
        result = provider.delete(project, application, stage, key)
        Configs.unregister_template_custom_render_path(key)
        return result

    def render(self, stage, filter=None):
        project = Configs.project
        application = Configs.application
        stage = Stages.normalize(stage)
        Logger.info(f"Start rendering templates: project={project}, application={application}, stage={Stages.shorten(stage)}")

        Logger.info("Loading secrets...")
        secrets = Secrets.list(stage, uninherited=False, decrypt=True)

        Logger.info("Loading parameters...")
        parameters = Parameters.list(stage, uninherited=False)

        Logger.info("Merging all parameters...")
        merged = deflatten_dict({x['Key']: x['Value'] for x in secrets['Secrets']})
        merge_dicts(deflatten_dict({x['Key']: x['Value'] for x in parameters['Parameters']}), merged)
        merge_dicts(Configs.meta_vars, merged)

        Logger.info("Loading templates...")
        templates = self.list(stage, filter=filter)['Templates']

        jinja_env = jinja2.Environment(undefined=jinja2.StrictUndefined)

        Logger.info("Rendering templates...")
        rendered = []
        for item in templates:
            key = item['Key']

            renderPath = item['RenderTo']
            if os.path.isdir(renderPath):
                raise DSOException("There is an existing directory at the template render path '{renderPath}'.")
            if os.path.dirname(renderPath):
                os.makedirs(os.path.dirname(renderPath), exist_ok=True)

            try:
                template = jinja_env.from_string(self.get(stage, key)['Contents'])
            except:
                Logger.error(f"Failed to load template: {key}")
                raise
            # undeclaredParams = jinja2.meta.find_undeclared_variables(env.parse(template))
            # if len(undeclaredParams) > 0:
            #     Logger.warn(f"Undecalared parameter(s) found:\n{set(undeclaredParams)}")
            try:
                Logger.debug(f"Rendering template: key={key}, render_path={renderPath}")
                renderedContent = template.render(merged)
            except Exception as e:
                Logger.error(f"Failed to render template: {key}")
                msg = getattr(e, 'message', getattr(e, 'msg', str(e)))
                raise DSOException(msg)

            with open(renderPath, 'w', encoding='utf-8') as f:
                f.write(renderedContent)
            
            rendered.append({
                        'Key':key, 
                        'Scope': item['Scope'],
                        # 'Origin': item['Origin'],
                        'RenderTo': renderPath,
                        })

        return rendered


Templates = TemplateManager()