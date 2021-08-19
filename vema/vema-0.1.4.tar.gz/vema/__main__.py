import argparse
import os
import re

from . import Vema
from .src import cli

parser = argparse.ArgumentParser(description="Vema manager");
parser.add_argument("-generate", action="store_true", default=False, help="It generates the directory and the minimum files to be able to work.");
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

if args.generate:
    cli.generate_structure();
    print("The minimum structure has been generated");

if args.createRouters:
    cli.generate_routers();
    print("Routes have been generated.");

if args.domain != None:
    if re.match("https{0,}://[a-zA-Z]*.[a-zA-Z]{2,}", args.domain):
        app = Vema(args.domain);
        print("Building the static pages...");
        
        if os.path.exists("routers.py"):
            cli.generate_routers()
        app.compile();

        print("Static pages have already been generated.");
    else:
        print("A valid domain name is required.");

if args.namePage != None:
    if len(args.namePage) > 2:
        if args.namePage.endswith(".html"):
            cli.createPage(args.namePage);
            print("The correct page has been created.");
        elif args.namePage.endswith(".md"):
            cli.createPage(args.namePage, ".md");
            print("The correct page has been created.");
        else:
            print("The extension is not correct");

if args.namePost != None:
    if len(args.namePost) > 2:
        if args.namePost.endswith(".html"):
            cli.createPost(args.namePage);
            print("The correct page has been created.");
        elif args.namePost.endswith(".md"):
            cli.createPost(args.namePost, ".md");
            print("The correct page has been created.");
        else:
            print("The extension is not correct");
