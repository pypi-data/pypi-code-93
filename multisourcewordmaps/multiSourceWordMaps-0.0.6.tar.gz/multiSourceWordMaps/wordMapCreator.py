from multiSourceWordMaps.configEditor import ConfigEditor
from multiSourceWordMaps.extractor import Extractor
from multiSourceWordMaps.makeWordMap import MapCreator
from multiSourceWordMaps.getArgs import get_args
import os
import json

def main():
    args = get_args().parse_args()
    if(args.sub_command == "config"):
        configEditor = ConfigEditor()
        if(args.config_sub_command == "add"):
            configEditor.add_to_config(args)
        elif(args.config_sub_command == "remove"):
            configEditor.remove_from_config(args)
        elif(args.config_sub_command == "list"):
            configEditor.list_config()
    elif(args.sub_command == "make"):
        extractor = Extractor(args)
        makeMap = MapCreator(args)
        if(args.source):
            print(f"Making wordmap from {args.source}")
            extractor.pull_text_from_source()
            makeMap.make_map_from_text()
        else:
            print(f"Making wordmap for {args.ticker}")
            extractor.pull_text_for_ticker()
            makeMap.make_map_from_ticker()
            

if __name__ == "__main__":
    main()