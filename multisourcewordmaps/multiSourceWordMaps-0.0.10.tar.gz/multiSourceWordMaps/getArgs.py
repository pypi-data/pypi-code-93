import argparse

def get_args():
    parser = argparse.ArgumentParser(description="Allow user create word maps from cli")
    subparsers = parser.add_subparsers(dest="sub_command")
    
    # setup sub commands
    config = subparsers.add_parser('config', description="Used to edit batch source config", help="Used to interact with the list of source inputs")
    makeMap = subparsers.add_parser('make', description="Used to make word maps", help="Creates map from list of sources located in the config file")
    
    #setup config commands
    config_subparser = config.add_subparsers(help="Add/Remove/List config", dest="config_sub_command")
    config_add = config_subparser.add_parser('add', help="Add a source to the config")
    config_remove = config_subparser.add_parser('remove', help="Remove a source to the config")
    config_list = config_subparser.add_parser('list', help="List sources for a ticker")

    #setup config add command
    config_add.add_argument('ticker', help="Ticker that you want to add a soruce to")
    config_add.add_argument('source', help="Name of file or path to site you want extract from. \n If you give a file you can either use the --location flag to specify a path or you can manually add the file to PDFs/<ticker> ")
    config_add.add_argument('--location', help="Will copy the file at the location specified to your pdf's folder", required=False)

    #setup config remove command
    config_remove.add_argument('ticker', help="Ticker that you want to remove")
    config_remove.add_argument('source', help="Name of file you want to remove")

    #setup make command
    makeMap.add_argument('ticker', help="Ticker you want to make a map for", nargs="?")
    makeMap.add_argument('--source', help="If you want to make from a single source provide url or filepath.")

    return parser