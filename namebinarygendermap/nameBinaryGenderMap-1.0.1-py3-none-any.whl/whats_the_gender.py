import json 
import os

def whats_the_gender(name):

    # load the name:gender dictionary
    with open('./data/names_gender_dict.json', 'r') as f:
        names_gender_dict = json.load(f)

    # convert name to lowercase and lrstrip it
    q = name.lower().strip()

    # return gender if the name is in the dict
    if q in names_gender_dict.keys():
        return "the binary gender assigned to '{}' is '{}'".format(name, names_gender_dict[q]) 
    else:
        return "couldn't find the binary gender assigned to '{}'".format(name)