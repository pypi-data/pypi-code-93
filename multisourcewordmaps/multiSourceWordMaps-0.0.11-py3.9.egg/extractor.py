from pdfminer.high_level import extract_text
import requests
import re
from bs4 import BeautifulSoup
from multiSourceWordMaps.configEditor import ConfigEditor
from multiSourceWordMaps.utils import create_text_file_path, create_pdf_file_path, is_website

class Extractor:

    def __init__(self, args):
        self.config = ConfigEditor().config
        self.source = args.source # path for pdf, url for website
        self.ticker = args.ticker
        return

    def pull_text_from_source(self):
        if is_website(self.source):
            self.extract_from_website_to_text()
        else:
            self.extract_from_pdf_to_text()           

    def pull_text_for_ticker(self):
        ticker_sources = self.config["sources"][self.ticker]
        for source in ticker_sources:
            self.source = source
            self.pull_text_from_source()
            
    def extract_from_pdf_to_text(self):
        pdf_path = create_pdf_file_path(
            self.config["package_dir"],
            self.ticker,
            self.source
        )
        print(f"Opening PDF: {pdf_path}")
        form_feed = re.compile('')
        non_alpha_numeric = re.compile('[^a-zA-Z ]')
        text = form_feed.sub('', extract_text(pdf_path))
        filtered_text = non_alpha_numeric.sub('', text)
        outPath = create_text_file_path(
                self.config["package_dir"],
                self.ticker,
                self.source
            )
        textOutFile = open(outPath,"w+")
        print(f"Writing2 to text file: {outPath}")
        textOutFile.write(filtered_text)
        textOutFile.close()

    def extract_from_website_to_text(self):
        url = self.source
        if (len(url.split("http")) <= 1):
            url = f"http://{url}"
        doc = requests.get(url).text
        outPath = create_text_file_path(
            self.config["package_dir"],
            self.ticker,
            self.source
        )
        self.parse_text_from_html(doc)
        textOutFile = open(outPath,"w+")
        print(f"Writing to text file: {outPath}")
        textOutFile.write(self.parse_text_from_html(doc))
        textOutFile.close()

    def parse_text_from_html(self, doc):
        soup = BeautifulSoup(doc, features="html.parser")
        p_tags = soup.find_all('p')
        h_tags = soup.find_all(re.compile('^h[1-6]$'))
        all_text  = []
        for p_tag in p_tags:
            all_text.append(p_tag.text)
        for h_tag in h_tags:
            all_text.append(h_tag.text)

        return " ".join(all_text)





