import click
import output.pushtoES as op
import os
import yaml
import time
import schedule
import sys
import input.etl as inp


@click.command()
@click.argument("config_path", default='', required=False)
def main(config_path):

    config = {}
    try:
        # if os.path.isfile("config.yaml"):
        with open(config_path) as file:
            config = yaml.load(file)
                # logger.info(config)
    except Exception as exception:
  
        print("error in opening config.yaml")



    res = []

    #for metric in config.get("metrics",{}).get("plugins"):
        #exec("from input import %s" %metric["name"])
        #metric_data = eval(metric["name"]+".work")(metric)
    metric_data = inp.work(config,config_path)
    
    for doc in metric_data:
        doc["_plugin"] =  "etlReport"
        doc["_documentType"]  = doc["type"]
        doc["_tag_Name"] = config.get("tags",{}).get("Name","")
        doc["_tag_appName"] = config.get("tags",{}).get("appName","")
        doc["_tag_projectName"] = config.get("tags",{}).get("projectName","")
        doc["time"] = int(time.time() * 1000)
    if sys.version_info[0] < 3:
        metric_data = [op.iterateDict(i) for i in metric_data]
    res.append(op.write_docs_bulk(config,metric_data))
            




