from pathlib import Path
from yaml import load, Loader

class Config:
    def __init__(self, path: Path = None) -> None:
        if path is None:
            self.config_path = Path.home().joinpath(".stakenix").joinpath("config.yaml")
        else:
            self.config_path = path
    
    def get_config(self) -> dict:
        with open(self.config_path, 'r') as file:
            return load(file, Loader=Loader)