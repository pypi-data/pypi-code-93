import json
from pathlib import Path


def swagger_file_to_sql_alchemy_orm_classes(file_path: Path):  # ToDo test and perhaps publish into a spereate app
    classes = []
    with open(file_path, "r") as file:
        spec = json.load(file)
        for path, value in spec["paths"].items():
            if value.get("get"):
                responses = value["get"]["responses"]
            elif value.get("post"):
                responses = value["post"]["responses"]
            if responses.get("200"):
                schema = responses["200"]["schema"]
                klass = []
                if schema.get("properties"):
                    for name, desc in schema["properties"].items():
                        if desc.get("format"):
                            klass.append({"name": name, "format": desc["format"], "type": desc["type"]})
                        else:
                            klass.append({"name": name, "format": None, "type": desc["type"]})
                elif schema.get("items"):
                    if schema.get("items").get("properties"):
                        for name, desc in schema["items"]["properties"].items():
                            if desc.get("format"):
                                klass.append({"name": name, "format": desc["format"], "type": desc["type"]})
                            else:
                                klass.append({"name": name, "format": None, "type": desc["type"]})
                classes.append({"path": path, "klass": klass})

    with open("sample_orms.py", "w") as output:
        for klass in classes:
            output.write("class {}(Base):\n".format(klass["path"]))
            output.write("    __tablename__ = {}\n\n".format(klass["path"]))
            for name_and_type in klass["klass"]:
                output.write("    {} =".format(name_and_type["name"]))
                if name_and_type["format"] == "date-time":
                    output.write(" Column(DateTime)\n")
                elif name_and_type["format"] == "date":
                    output.write(" Column(Date)\n")
                elif name_and_type["format"] in ("int32", "int64"):
                    output.write(" Column(Integer)\n")
                elif name_and_type["format"] == "string":
                    output.write(" Column(String)\n")
                elif name_and_type["format"] in ("float", "double"):
                    output.write(" Column(Float)\n")
                elif name_and_type["format"] is None:
                    if name_and_type["type"] == "string":
                        output.write(" Column(String)\n")
                    elif name_and_type["type"] == "integer":
                        output.write(" Column(Integer)\n")
                    elif name_and_type["type"] == "boolean":
                        output.write(" Column(Boolean)\n")
                    elif name_and_type["type"] == "object":
                        output.write(" Column(Object)\n")  # ToDo objects
                    elif name_and_type["type"] == "array":
                        output.write(" Column(Array)\n")  # ToDo arrays
                    else:
                        print(klass["path"])
                        print(name_and_type["name"])
                        print(name_and_type["type"])
                else:
                    print("Path: {}, Name: {}, Format: {}".format(klass["path"], name_and_type["name"],
                                                                  name_and_type["format"]))
            output.write("\n")
            output.write("    def __repr__(self):\n")
            output.write("        return '{}'.format({})\n".format(
                ", ".join(["{}={{}}".format(name_and_type["name"]) for name_and_type in klass["klass"]]),
                ", ".join(["self.{}".format(name_and_type["name"]) for name_and_type in klass["klass"]])))
            output.write("\n")
