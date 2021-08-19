import os

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
