#!/usr/bin/env python3

# imports
import os

# exceptions
## exception for if a section isnt found
class SectionNotFound(Exception):
    pass

## exception for if a key isnt found
class KeyNotFound(Exception):
    pass

## exception for if an invalid argument is provided
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
## find the start and end of a section.
def findSec(file, section):
    with open(file, "r") as f:
        fileContent = f.readlines()
    secStart, secEnd, fileLength = "none", "none", len(fileContent)
    for count, line in enumerate(fileContent):
        if line.strip() == f"[{section}]":
            secStart = count
            break
    if secStart == "none":
        raise SectionNotFound(f"{section} not found in {file}.")
    for count, line in enumerate(fileContent):
        if count > secStart:
            if line.strip().endswith("]") and line.strip().startswith("["):
                count2 = count
                while fileContent[count2].strip().endswith("]") and fileContent[count2].strip().startswith("[") and fileContent[count2] != "\n":
                    count2 -= 1
                secEnd = count2
                break
            elif fileLength - 1 == count:
                secEnd = count
                break
    if secEnd == "none":
        raise SectionNotFound(f"{section} not found in {file}.")
    return [ secStart, secEnd ]

# key functions
## find the location of a key.
def findKey(file, key, section):
    with open(file, "r") as f:
        fileContent = f.readlines()
    secEndStart, keyNumber = findSec(file, section), len(key) + 1
    for count, line in enumerate(fileContent):
        if count > secEndStart[0] and count <= secEndStart[1] and line.strip()[:keyNumber] == f"{key}=":
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
    fileContent[lineNum] = f"{key}={newValue}\n"
    with open(file, "w") as f:
        f.writelines(fileContent)

# functions for both types
## rename keys or sections
def rename(file, newName, section, **kwargs):
    key = kwargs.get("key")
    with open(file, "r") as f:
        fileContent = f.readlines()
    if not key:
        lineNum = findSec(file, section)[0]
        fileContent[lineNum] = fileContent[lineNum].replace(section, newName, 1)
    else:
        lineNum = findKey(file, key, section)
        fileContent[lineNum] = fileContent[lineNum].replace(key, newName, 1)
    with open(file, "w") as f:
        f.writelines(fileContent)

## add keys or sections
def add(file, **kwargs):
    key = kwargs.get("key")
    section = kwargs.get("section")
    value = kwargs.get("value")
    lineNum = kwargs.get("lineNum")
    with open(file, "r") as f:
        fileContent = f.readlines()
    fileLength = len(fileContent)
    if section and key and value:
        secEnd = findSec(file, section)[1]
        fileContent.insert(secEnd, f"{key}={value}\n")
    elif section and not key:
        fileContent.append(f"[{section}]\n")
    elif lineNum and section:
        if section and key and value:
            fileContent.insert(lineNum, f"{key}={value}\n")
        elif section and not key:
            fileContent.insert(lineNum, f"[{section}]\n")
    else:
        raise ReqArgNotFound("invalid arguments provided.")
    with open(file, "w") as f:
        f.writelines(fileContent)

## delete keys or sections
def delete(file, **kwargs):
    key = kwargs.get("key")
    section = kwargs.get("section")
    lineNum = kwargs.get("lineNum")
    with open(file, "r") as f:
        fileContent = f.readlines()
    if section and key:
        del fileContent[findKey(file, key, section)]
    elif section and not key:
        secEndStart = findSec(file, section)
        for count, line in enumerate(fileContent):
            if count >= secEndStart[0] and count <= secEndStart[1]:
                del fileContent[count]
    elif lineNum:
        del fileContent[lineNum - 1]
    else:
        raise ReqArgNotFound("invalid arguments provided.")
    with open(file, "w") as f:
        f.writelines(fileContent)
