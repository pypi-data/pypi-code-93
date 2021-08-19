import os
import pathlib

path_templates = str(pathlib.Path(__file__).parent.resolve()) + "/templates/";

def check_page_directory():
    if not os.path.exists("static/pages"):
        os.mkdir("static/pages");

def createPage(name, type=".html"):
    check_page_directory();

    with open(f"{path_templates}/template{type}", "r", encoding="UTF-8") as template:
        with open(f"static/pages/{name}", "w", encoding="UTF-8") as page:
            page.write(template.read());

def check_blog_directory():
    if not os.path.exists("static/blog"):
        os.mkdir("static/blog");

def createPost(name, type=".html"):
    check_blog_directory();

    with open(f"{path_templates}/template{type}", "r", encoding="UTF-8") as template:
        with open(f"static/blog/{name}", "w", encoding="UTF-8") as page:
            page.write(template.read());

def generate_structure():
    directories = [
        "static",
        "static/blog",
        "static/pages",
        "static/templates"
    ];

    for directory in directories:
        if not os.path.exists(directory):
            os.mkdir(directory);

    createPage("index.html");

    with open(f"{path_templates}/base.html", "r", encoding="UTF-8") as template:
        with open(f"static/templates/base.html", "w", encoding="UTF-8") as page:
            page.write(template.read());

def generate_routers():
    """
    Generates routers based on content
    """
    routers = "from vema import Page\n\n";
    routers += "def load_routers(app):\n";

    for root, _, files in os.walk("static"):
        for file in files:
            if "blog" in root or "pages" in root:
                if file.endswith(".html") or file.endswith(".md"):
                    routers += generate_route(root, file);

    with open("routers.py", "w") as file:
        file.write(routers);

def generate_route(path, name):
    """
    Generates a route based on the path
    """
    route = "\t@app.route("

    if name == "index.html":
        route += "'/')\n";
        route += "\tdef index():\n";
        route += f"\t\treturn Page('pages/{name}').render()\n\n";
        return route;

    if path.endswith("blog"):
        type_route = "blog";
    else:
        type_route = "pages"; 

    route += f"'/{type_route}/{name_to_uri(name)}')\n";
    route += f"\tdef {name_to_def(name)}():\n";
    route += f"\t\treturn Page('{type_route}/{name}').render()\n\n";

    return route;

def name_to_uri(name):
    """
    Transforms the name of a file into a URI
    """
    return name.split(".")[0].replace(" ", "-").lower();

def name_to_def(name):
    """
    Transforms the name of a file into a function name
    """
    return name.split(".")[0].replace(" ", "_").lower();
