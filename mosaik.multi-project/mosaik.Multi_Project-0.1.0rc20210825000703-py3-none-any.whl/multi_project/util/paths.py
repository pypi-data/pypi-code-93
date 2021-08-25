from pathlib import Path

ROOT_PATH = Path(__file__).parent.parent.parent.parent
DATA_PATH: Path = ROOT_PATH / 'data'
DATA_CONFIG_FILE_PATH = DATA_PATH / 'config.json'
