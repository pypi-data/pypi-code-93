import os
import json
import shutil
from multiSourceWordMaps.utils import is_website, create_pdf_file_path

class ConfigEditor:
    
    def __init__(self, package_path = None):
        try:
            if package_path:
                dist_dir = self.get_dist_dir()
                dist_dir = os.path.dirname(os.path.abspath(__file__))
                config_path = f"{dist_dir}/config.py"
                with open(config_path, "r") as config_file:
                    config = json.load(config_file)
                config["package_dir"] = package_path
                with open(config_path, "w+") as config_file:
                    config_file.write(json.dumps(config))
                self.config = config
            else:
                self.config = self.get_config()

        except FileNotFoundError:
            raise FileNotFoundError (f"Config file not found.")

    def add_to_config(self,args):
        ticker,location,source = args.ticker,args.location,args.source
        locationString = location or ""
        sources = self.config["sources"]
        if ticker not in sources:
            sources[ticker] = []
        if source in sources[ticker]:
            print(f"{source} is already in the sources list for {ticker}.")
            return

        print(f"Adding {source} {locationString} to {ticker} folder test")
        sources[ticker].append(source)
        self.config["sources"] = sources

        package_dir = self.config["package_dir"]
        if location:
            if not os.path.exists(location):
                raise FileNotFoundError(f"Could not find file at : {location}. Did not add to config.")
            if is_website(source):
                raise BaseException("Can not specify location for website.")
            print(f"Package dir {package_dir}")
            pdf_path = create_pdf_file_path(
                        self.config["package_dir"],
                        ticker,
                        source
                    )
            mkdir_path = pdf_path.split("/")[:-1]
            dest_no_file = "/".join(mkdir_path)
            os.makedirs(dest_no_file, exist_ok = True)
            shutil.copyfile(location,pdf_path)
            print(f"Copying file \nFrom:{location} \nTo:{pdf_path}")

                
        self.write_config(self.config)

    def remove_from_config(self, args):
        source,ticker = args.source, args.ticker
        print(f"Removing {source} from {ticker} folder")
        sources = self.config["sources"]
        if ticker in sources:
            if source in sources[ticker]:
                sources[ticker].remove(source)
                if sources[ticker] == []:
                    print(f"No files left, removing {ticker} folder from config.")
                    del sources[ticker]
                if not is_website(source):
                    pdf_path = create_pdf_file_path(
                        self.config["package_dir"],
                        ticker,
                        source
                    )
                    if os.path.exists(pdf_path):
                        os.remove(pdf_path)
                        if len(os.listdir(os.path.dirname(pdf_path))) == 0:
                            os.rmdir(os.path.dirname(pdf_path))

            else:
                raise BaseException(f"{source} not in {ticker}")
        else:
            raise BaseException(f"{ticker} not in sources")
        self.write_config()

    def list_config(self):
        print("Config:")
        for ticker in self.config["sources"]:
            print(f"\n\t{ticker}:")
            for source in self.config["sources"][ticker]:
                print(f"\n\t   {source}")

    def get_config(self):
        config_path = f"{self.get_dist_dir()}/config.py"
        with open(config_path,'r') as config_file:
            config = json.load(config_file)

        return config

    def write_config(self, config = None):
        config_path = f"{self.get_dist_dir()}/config.py"
        upper_config_path = f"{self.config['package_dir']}/multiSourceWordMaps/config.py"
        with open(config_path,'w') as config_file:
            with open(upper_config_path,'w') as upper_config_file:
                if not config:
                    config_file.write(json.dumps(self.config)) 
                    upper_config_file.write(json.dumps(self.config)) 
                else:
                    config_file.write(json.dumps(config))
                    upper_config_file.write(json.dumps(config))

    #Makes mocking for tests easier.
    def get_dist_dir(self):
        return os.path.dirname(os.path.abspath(__file__))

            
