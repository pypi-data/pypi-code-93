from jinja2 import Environment, FileSystemLoader, StrictUndefined, TemplateNotFound


class TemplateLoader:
    def __init__(self, templates_folder):
        self.env = Environment(
            loader=FileSystemLoader(templates_folder), undefined=StrictUndefined
        )

    def has_template(self, template_name):
        try:
            self.get_template(template_name)
        except TemplateNotFound:
            return False
        else:
            return True

    def get_template(self, template_name):
        return self.env.get_template(template_name)
