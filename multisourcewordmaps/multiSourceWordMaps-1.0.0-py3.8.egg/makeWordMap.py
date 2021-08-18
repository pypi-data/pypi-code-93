from wordcloud import WordCloud
from multiSourceWordMaps.configEditor import ConfigEditor
from multiSourceWordMaps.utils import create_png_file_path, create_text_file_path

class MapCreator:

    def __init__(self,args):
        self.config = ConfigEditor().config
        self.ticker = args.ticker
        self.source = args.source

    def make_map_from_ticker(self):
        sources = self.config["sources"][self.ticker]
        for source in sources:
            self.source = source
            self.make_map_from_text()

    def make_map_from_text(self):
        text_path = create_text_file_path(
            self.config["data_dir"],
            self.ticker,
            self.source
        )
        png_path = create_png_file_path(
            self.config["data_dir"],
            self.ticker,
            self.source
        )
        self.makeWordMap(text_path, png_path)
        return

    def makeWordMap(self, text_path, png_path):
        with open(text_path,"r") as readFile:
            text = readFile.read()
        wordcloud = WordCloud().generate(text)
        wordcloudImage = wordcloud.to_image()
        wordcloudImage.save(png_path)
        print(f"Creating map: {png_path}")
