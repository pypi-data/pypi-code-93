import numpy as np
import pandas as pd
import base64
import os
import pytesseract
import pandas as pd
from pdf2image import *
import PIL
import re
from PyPDF3 import PdfFileWriter, PdfFileReader
import io
#Import the garbage collection module

def populate_csv(files):
    page_ids = []
    #list of all documents
    page_texts = []
    for open_file in files:
        page_ids.append(open_file.name)
        inputpdf = PdfFileReader(io.BytesIO(open_file.getvalue()))
        maxPages = inputpdf.numPages
        image_counter = 1
        for page in range(1, maxPages, 10):
            try:
                images = convert_from_bytes(open_file.getvalue(), first_page=page, last_page=min(page + 10 - 1, maxPages))
                for image in images:
                    image.save('page' + str(image_counter) + '.jpg', 'jpeg')
                    image_counter += 1
            except exceptions.PDFPageCountError as error:
                st.write("Error:")
                st.write(page)
                continue
            

        filelimit = image_counter - 1
        #list of each document
        individual = []
        # read the images generated, and turn into csv using ocr
        for i in range(1, image_counter):
            filename = "page" + str(i) + ".jpg"
            text = pytesseract.image_to_string(PIL.Image.open(filename))
            text.replace("\n'", " ")
            individual += [text]
            if os.path.isfile(filename):
                os.remove(filename)
            else:    ## Show an error ##
                print("Error: %s file not found" % filename)
        page_texts.append(individual)
        
    csv = pd.DataFrame(data={
        'page_ids': page_ids,
        'page_texts': page_texts
    }).to_csv(index=False)
    return csv