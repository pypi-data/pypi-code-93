import os

### read values of keys
def vsmlRead(mode, section, key, file):
    keyLine, secLine, valueLine = 0, 0, ""
    with open(file, "r") as f:
        fileContent = f.readlines()
    for count, line in enumerate(fileContent):
        if line == "[" + section + "]":
            secLine = count
            break
    for count, line in enumerate(fileContent):
        if key in line and count > secLine:
            keyLine, valueLine = count, line
            break
    value = valueLine.replace(key + "=", "")
    if mode == "text":
        return value
    elif mode == "lineInfo":
        return [keyLine, valueLine]

### change values of keys
def vsmlEdit(**kwargs):
    with open(kwargs.get("file"), "r") as f:
        fileContent = f.readlines()
    fileContent[int(vsmlRead("lineInfo", kwargs.get("section"), kwargs.get("key"), kwargs.get("file"))[0]) - 1] = kwargs.get("key") + "=" + kwargs.get("newValue")
    fileContent = "\n".join(fileContent)
    with open(kwargs.get("file"), "w") as f:
        f.writelines(fileContent)

### rename keys or sections
def vsmlRename(**kwargs):
    with open(str(kwargs.get("file")), "r") as f:
        fileContent = f.readlines()
    if "section" in kwargs and "not key" in kwargs:
        fileContent[fileContent.index("[" + str(kwargs.get("section")) + "]")] = "[" + str(kwargs.get("newName")) + "]"
    elif "key" in kwargs and "section" in kwargs:
        info = vsmlRead("lineInfo", kwargs.get("section"), kwargs.get("key"), str(kwargs.get("file")))
        fileContent[int(info[0])] = str(info[1]).replace(str(kwargs.get("key")), str(kwargs.get("newName")))
    with open(str(kwargs.get("file")), "w") as f:
        fileContent = "\n".join(fileContent)
        f.writelines(fileContent)

### strip to remove all whitespaces
def vsmlStrip(**kwargs):
    if "file" in kwargs:
        if os.path.isfile(kwargs.get("file")):
            with open(kwargs.get("file"), "r") as f:
                lines = f.readlines()
            with open(kwargs.get("file"), "w") as f:
                for a in [b.strip() for b in lines]:
                    f.write(a + "\n")
        else:
            print("error: file does not exist.")
    else:
        print("error: file path not provided.")

### add keys or sections
def vsmlAdd(**kwargs):
    if "file" in kwargs:
        if os.path.isfile(kwargs.get("file")):
            with open(kwargs.get("file"), "r+") as f:
                if kwargs.get("type") == "num":
                    pass
                elif kwargs.get("type") == "section":
                    f.write("\n" + "[" + kwargs.get("name") + "]")
                elif kwargs.get("type") == "key":
                    if "value" in kwargs:
                        f.write("\n" + kwargs.get("name") + "=" + kwargs.get("value"))
                    else:
                        print("error: value argument not provided (required if type argument is equal to 'key')")
                else:
                    print("error: provided type argument not equal to either 'num', 'section', or 'key'")
        else:
            print("error: file does not exist.")
    else:
        print("error: file path not provided.")
        print("required arguments: file, type, name (value also required if type argument is equal to 'key')")

### delete keys or sections
def vsmlDelete(**kwargs):
    # required arguments: file, num OR section OR key (section is also required if using key)
    with open(str(kwargs.get("file")), "r") as f:
        content = f.readlines()
    if "num" in kwargs:
        del content[kwargs.get("num") - 1]
    elif "section" in kwargs and not "key" in kwargs:
        value = "[" + str(kwargs.get("section")) + "]"
        content.remove(value)
    elif "key" in kwargs and "section" in kwargs:
        info = vsmlRead("lineInfo", kwargs.get("section"), kwargs.get("key"), str(kwargs.get("file")))
        del content[int(info[0]) - 1]
    with open(str(kwargs.get("file")), "w") as f:
        f.writelines(content)

