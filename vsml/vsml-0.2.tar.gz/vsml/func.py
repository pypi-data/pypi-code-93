#!/usr/bin/env python3

# imports
import os

# exceptions
### exception for if a section isnt found
class SectionNotFound(Exception):
    pass

### exception for if a key isnt found
class KeyNotFound(Exception):
    pass

### exception for if an invalid argument is provided
class ReqArgNotFound(Exception):
    pass

# file functions
## check if file exists or is inaccessible for a specific reason, and strip file of whitespace.
def initFile(file):
    if os.path.isfile(file):
        if os.access(file, os.W_OK):
            with open(file, "r") as f:
                fileContent = f.readlines()
            for count, line in enumerate(fileContent):
                fileContent[count] = f"{line.strip()}\n"
            with open(file, "w") as f:
                f.writelines(fileContent)
        else:
            raise PermissionError(f"no permission to write to {file}.")
    else:
        raise IOError(f"{file} does not exist.")

# section functions
## find the start of a section.
def findSecStart(file, section):
    with open(file, "r") as f:
        fileContent = f.readlines()
    for count, line in enumerate(fileContent):
        if line.strip() == f"[{section}]":
            return count
    raise SectionNotFound(f"{section} not found in {file}.")

## find the end of a section.
def findSecEnd(file, section):
    with open(file, "r") as f:
        fileContent = f.readlines()
    secStart = findSecStart(file, section)
    for count, line in enumerate(fileContent):
        if count > secStart:
            try:
                if fileContent[count + 1] == "\n" and fileContent[count + 2].strip().endswith("]") and fileContent[count + 2].strip().startswith("["):
                    return count
            except IndexError:
                return count
    raise SectionNotFound(f"{section} not found in {file}.")

# key functions
## find the location of a key.
def findKey(file, key, section):
    with open(file, "r") as f:
        fileContent = f.readlines()
    secStart, secEnd, keyNumber = findSecStart(file, section), findSecEnd(file, section), len(key) + 1
    for count, line in enumerate(fileContent):
        if count > secStart and count <= secEnd and line.strip()[:keyNumber] == f"{key}=":
            return count
    raise KeyNotFound(f"{key} not found in {file}.")

## read the values of keys.
def readKeyValue(file, key, section):
    with open(file, "r") as f:
        fileContent = f.readlines()
    return fileContent[findKey(file, key, section)].strip().replace(f"{key}=", "", 1)

## change the values of keys.
def editKeyValue(file, key, newValue, section):
    with open(file, "r") as f:
        fileContent = f.readlines()
    lineNum = findKey(file, key, section)
    if len(fileContent) == lineNum:
        fileContent[lineNum] = f"{key}={newValue}"
    else:
        fileContent[lineNum] = f"{key}={newValue}\n"
    with open(file, "w") as f:
        f.writelines(fileContent)

# functions for both types
## rename keys or sections
### optional kwargs: key="<old key name>" (for renaming a key)
def rename(file, newName, section, **kwargs):
    key = kwargs.get("key")
    with open(file, "r") as f:
        fileContent = f.readlines()
    if not key:
        fileContent[findSecStart(file, section)] = f"[{newName}]"
    else:
        lineNum = findKey(file, key, section)
        fileContent[lineNum] = fileContent[lineNum].replace(key, newName, 1)
    with open(file, "w") as f:
        f.writelines(fileContent)

## add keys or sections
### 1 or more required kwargs: lineNum, section, or key AND value
def add(file, **kwargs):
    key = kwargs.get("key")
    section = kwargs.get("section")
    value = kwargs.get("value")
    lineNum = kwargs.get("lineNum")
    with open(file, "r") as f:
        fileContent = f.readlines()
    if lineNum:
        if section and key and value:
            try:
                fileContent.insert(lineNum, f"{key}={value}\n")
            except IndexError:
                fileContent.append(f"{key}={value}\n")
        elif section and not key:
            fileContent.insert(lineNum, f"[{section}]\n")
    elif section and key and value:
        secEnd = findSecEnd(file, section)
        try:
            fileContent.insert(secEnd + 1, f"{key}={value}\n")
        except IndexError:
            fileContent.append(f"{key}={value}\n")
    elif section and not key:
        fileContent.append("\n")
        fileContent.append(f"[{section}]")
    elif not lineNum and not section and not value and not key:
        raise ReqArgNotFound("lineNum, section, or section + key + value arguments must be provided.")
    elif section and key and not value:
        raise ReqArgNotFound("value argument must be provided if key argument is provided.")
    with open(file, "w") as f:
        f.writelines(fileContent)

## delete keys or sections
### 1 or more required kwargs: lineNum, section, or section + key
def delete(file, **kwargs):
    key = kwargs.get("key")
    section = kwargs.get("section")
    lineNum = kwargs.get("lineNum")
    with open(file, "r") as f:
        fileContent = f.readlines()
    if lineNum:
        del fileContent[lineNum - 1]
    elif section and not key:
        fileContent.remove(f"[{section}]")
    elif key and section:
        del fileContent[findKey(file, key, section)]
    elif key and not section:
        raise ReqArgNotFound("section argument must be provided if key argument is provided.")
    else:
        raise ReqArgNotFound("lineNum, section, or section + key arguments must be provided.")
    with open(file, "w") as f:
        f.writelines(fileContent)
