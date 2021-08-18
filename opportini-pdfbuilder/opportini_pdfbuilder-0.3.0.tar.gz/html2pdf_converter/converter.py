# coding: utf-8
import argparse
import os
import json
import sys
import platform

from jinja2 import Template


from html2pdf_converter.tools.html_to_pdf_converter import (
    get_pdf_from_html,
    get_html_name,
    get_pdf_name,
)
from html2pdf_converter.tools.random_names import produce_amount_names


parser = argparse.ArgumentParser()
parser.add_argument(
    '--engine', '-e', type=int,
    help="0 - chromium, 1 - prince, 2 - xhtml2pdf"
)
parser.add_argument(
    '--json', '-j', type=str,
    help="path to json file"
)
parser.add_argument(
    '--template_id', '-tid', type=str,
    help="Id of template: jrnl, jrnl-cover"
)
parser.add_argument(
    '--output', '-o', type=str,
    help="path to render pdf file"
)
parser.add_argument(
    '--html_only', type=bool,
    help="create html file, not render pdf file"
)
parser.add_argument(
    '--from_html', type=int, 
    help="create pdf from HTML directly"
)
parser.add_argument(
    '--html_file', type=str, 
    help="html file path"
)
parser.add_argument(
    '--temp_html_base_dir', type=str, 
    help="template html file path"
)

is_python2 = platform.python_version().startswith('2.7')


class HtmlToPdfConverter:
    """
    The CLASS where we get JSON data and template
    create temp HTML file
    convert HTML to PDF
    For more details read the README file
    """

    def __init__(
        self,
        base_dir=None,
        engine=0,
        json_data=None,
        json_file_path=None,
        html_data=None,
        html_template_path=None,
        html_only=False,
        from_html=True,
        html_file=None,
        temp_html_base_dir=None
    ):
        self.engine = engine
        self.json_data = json_data
        self.json_file_path = json_file_path
        self.html_data = html_data
        self.html_template_path = html_template_path
        self.base_dir = base_dir or os.path.abspath(os.path.join(
            os.path.dirname(os.path.dirname(__file__))))
        self.assets_dir = os.path.join(self.base_dir, 'assets/')
        self.static_url = os.path.join(self.base_dir, 'static/')
        self.chromium_path = os.path.join(self.assets_dir, 'drivers/')
        self.html_only_mode = html_only
        self.from_html = from_html
        self.html_file = html_file
        self.temp_html_base_dir = temp_html_base_dir

    def get_chromium_driver(self):
        _type = sys.platform
        if _type in ('linux', 'linux2'):
            return os.path.join(self.chromium_path, 'linux-chromedriver')

        if _type == 'darwin':
            return os.path.join(self.chromium_path, 'mac-chromedriver')

        if _type == 'win32':
            return os.path.join(self.chromium_path, 'chromedriver.exe')

    def get_json(self):
        if self.json_file_path:
            with open(os.path.abspath(self.json_file_path)) as json_file:
                return json.loads(str(json_file.read()))
        return json.loads((self.json_data))

    def render_template(self, json_data=None):
        """Get template by path"""
        # file_loader = FileSystemLoader('templates')
        # env = Environment(loader=file_loader)
        _path = os.path.join(
            self.base_dir,
            'templates',
            # self.html_template_path
            'void-report.html'
        )
        with open(os.path.abspath(_path)) as html_file:
            self.html_data = html_file.read()

        if is_python2:
            self.html_data = self.html_data.decode('utf-8')

        return Template(self.html_data).render(
            json_obj=json_data,
            static_url=self.static_url
        )

    @staticmethod
    def create_temp_html_file(rendered_html=None, base_dir=None):
        """
        Write rendered template to temp html
        """
        if is_python2:
            rendered_html = rendered_html.encode('utf-8')

        _name = get_html_name(list(produce_amount_names(1))[0])
        path = f"{base_dir}/{_name}"
        with open(path, "w") as file:
            file.write(rendered_html)  # Write HTML String to temp html
            return file.name

    def get_pdf_file(self, temp_html_file_path, output_file=None):
        """Get pdf file"""
        html_path = 'file://' + temp_html_file_path
        return get_pdf_from_html(
            path=html_path, chromedriver=self.get_chromium_driver(),
            pdf_file_path=output_file, engine=self.engine)

    def write_pdf_file(self, temp_html_file_path, output_file):
        if self.html_only_mode:
            return

        if self.engine == 1:
            self.get_pdf_file(temp_html_file_path, output_file)
        else:
            with open(output_file, 'wb') as file:
                file.write(self.get_pdf_file(temp_html_file_path))
        print(temp_html_file_path)
        os.remove(temp_html_file_path)

    def get_html(self):
        json_data = self.get_json()
        rendered_html = self.render_template(json_data)

        return rendered_html

    def create(self, output_file=None):
        print(self.from_html)
        if self.from_html == 0:
            html = self.get_html()
            temp_html_file_path = self.create_temp_html_file(html, self.temp_html_base_dir)
        else:
            temp_html_file_path = self.html_file

        if not output_file:
            # using function for generate random name
            output_file = list(produce_amount_names(1))[0]
            output_file = get_pdf_name(self.assets_dir, output_file)

        # print(str('./' + temp_html_file_path))
        if os.path.isfile(temp_html_file_path):
            self.write_pdf_file(
                temp_html_file_path=temp_html_file_path,
                output_file=output_file
            )

        return output_file


if __name__ == "__main__":
    args = parser.parse_args()
    html_to_pdf_obj = HtmlToPdfConverter(
        engine=args.engine,
        json_file_path=args.json,  # 'assets/book.json'
        json_data=json.dumps({
            "name": "qqqq",
            "description": "wwww",
            "price": 123
        }),
        # html_template_path=templates.get(args.template_id),
        html_data='<div class="container">'
        '<div class="row"><div class="col-lg-12 text-center">'
        '<h1 class="mt-5">{{ json_obj.name }}</h1>'
        '<p class="lead">{{ json_obj.description }}</p>'
        '<p class="lead">{{ json_obj.price }}</p></div></div></div>',
        html_only=args.html_only or False,
        from_html=args.from_html,
        html_file=args.html_file,
        temp_html_base_dir=args.temp_html_base_dir
    )
    html_to_pdf_obj.create(
        output_file=args.output
    )
