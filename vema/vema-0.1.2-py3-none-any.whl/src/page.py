import os

from flask import render_template
from .exceptions.wrongPath import WrongPath
from .exceptions.wrongExtension import WrongExtension

class Page:
    def __init__(self, path, template="templates/base.html", **kwargs):
        self.path = path;
        self.template = template;
        self.kwargs = kwargs;
        
        if not os.path.exists("static/" + self.path):
            raise WrongPath("static/" + self.path);
        if not os.path.exists("static/" + template):
            raise WrongPath("static/" + template);

        if self.path.endswith(".md"):
            self.load_data_md();

    def load_data_md(self) -> None:
        self.properties = {};
        self.end_position_properties = 0;

        with open("static/" + self.path) as file:
            linea = file.readline();

            while linea != "" and ":" in linea:
                data = linea.split(":");
                self.end_position_properties += len(linea);

                self.properties.update({data[0].strip(): data[1].strip()});

                linea = file.readline();

            file.seek(self.end_position_properties);
            self.content = file.read();

    def render(self) -> str:
        if self.path.endswith(".html"):
            return render_template(self.path, **self.kwargs);
        elif self.path.endswith(".md"):
            return render_template(self.template, properties=self.properties, content=self.content, **self.kwargs);
        else:
            raise WrongExtension(self.path.split(".")[-1]);