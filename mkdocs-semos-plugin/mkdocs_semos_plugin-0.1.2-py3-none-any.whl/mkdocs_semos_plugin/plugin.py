import os
import sys
import re
from pathlib import Path
from timeit import default_timer as timer
from datetime import datetime, timedelta

from mkdocs import utils as mkdocs_utils
from mkdocs.config import config_options, Config
from mkdocs.plugins import BasePlugin

class SemosPlugin(BasePlugin):

    config_scheme = (
        ('param', config_options.Type(str, default='')),
    )

    def __init__(self):
        self.enabled = True
        self.total_time = 0

    def on_page_content(self, html, page, config, files):
        #print(config, files)
        img_regex = '<img(.*?)\/>'
        src_regex = 'src="(.*?)"'

        img = re.compile(img_regex)
        src = re.compile(src_regex)

        for item in img.finditer(html):
            src_match = src.search(item.group())

            if src_match:
                print(item.start(), item.group())
                #print(src_match.group(1))
                
                # <img alt="Diagrama solucion!" src="imgs/aws.drawio.svg" title="Diagrama Solución" />
                # <object data="imgs/componentes.drawio.svg" type="image/svg+xml" id="svg" width="100%" height="100%"></object>
                html = html.replace(item.group(), f"<object data=\"{src_match.group(1)}\" type=\"image/svg+xml\" id=\"svg\" width=\"100%\" height=\"100%\"></object>")

        return html

    def on_post_build(self, config):
        build_dir = config['site_dir']

        print('temp dir: ', build_dir)

        for svg in Path(build_dir).rglob('*.svg'):
            if svg.suffix == '.svg':
                print(svg)

            content = svg.read_text()
            svg.write_text(content.replace('<a xlink', '<a target="_parent" xlink'))

        return

#    def on_serve(self, server):
#        return server

#    def on_pre_build(self, config):
#        return
#
#    def on_files(self, files, config):
#        return files
#
#    def on_nav(self, nav, config, files):
#        return nav
#
#    def on_env(self, env, config, files):
#        return env
#    
#    def on_config(self, config):
#        return config
#
#    def on_pre_template(self, template, template_name, config):
#        return template
#
#    def on_template_context(self, context, template_name, config):
#        return context
#    
#    def on_post_template(self, output_content, template_name, config):
#        return output_content
#    
#    def on_pre_page(self, page, config, files):
#        return page
#
#    def on_page_read_source(self, page, config):
#        return ""
#
#    def on_page_markdown(self, markdown, page, config, files):
#        return markdown
#
#    def on_page_content(self, html, page, config, files):
#        return html 
#
#    def on_page_context(self, context, page, config, nav):
#        return context
#
#    def on_post_page(self, output_content, page, config):
#        return output_content

