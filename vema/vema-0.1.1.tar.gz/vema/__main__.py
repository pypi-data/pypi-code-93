import argparse
import os
import re

from . import Vema
from .src import routers

parser = argparse.ArgumentParser(description="Vema manager");
parser.add_argument("-dev", action="store_true", default=False, help="Launch web server. [debug mode]");
parser.add_argument("-start", action="store_true", default=False, help="Launch web server.");
parser.add_argument("-build", action="store", dest="domain", help="Build static pages.");
parser.add_argument("-createRouters", action="store_true", help="Generates the development routes. Important: overwrite the file changes!");
parser.add_argument("-createPage", action="store", dest="namePage", help="Create a new page.");
parser.add_argument("-createPost", action="store", dest="namePost", help="Create a new post.");

args = parser.parse_args();

if args.start:
    app = Vema();
    app.run();

if args.dev:
    app = Vema();
    app.run(debug=True);

if args.createRouters:
    routers.generate_routers();
    print("Routes have been generated.");

if args.domain != None:
    if re.match("https{0,}://[a-zA-Z]*.[a-zA-Z]{2,}", args.domain):
        app = Vema(args.domain);
        print("Building the static pages...");
        
        if os.path.exists("routers.py"):
            routers.generate_routers()
        app.compile();

        print("Static pages have already been generated.");
    else:
        print("A valid domain name is required.");

if args.namePage != None:
    if len(args.namePage) > 2:
        if not os.path.exists("static/pages"):
            os.mkdir("static/pages");
        with open(f"static/pages/{args.namePage}", "w", encoding="UTF-8") as file:
            text = """<!DOCTYPE html>
    <html lang="en">
        <head>
            <meta charset="UTF-8">
            <title>Title</title>
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <meta name="description" content="">
            <meta name="author" content="">
        </head>
        <body>
            <h1>This is a test page</h1>
    </body>
    </html>""";
            file.write(text);

if args.namePost != None:
    if len(args.namePost) > 2:
        if not os.path.exists("static/blog"):
            os.mkdir("static/blog");
        with open(f"static/blog/{args.namePost}", "w", encoding="UTF-8") as file:
            text = """title:This is a test
description:This is a test description
date:15/08/2021

# This is a test

This is a test description""";
            file.write(text);