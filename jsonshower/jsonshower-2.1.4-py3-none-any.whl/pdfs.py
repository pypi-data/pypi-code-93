"""Module for showing PDFs
"""
import time
import requests
import os
from pdf2image import convert_from_path
from pdf_annotate import PdfAnnotator, Location, Appearance
from IPython.display import display


def show_pdf_from_json(results, pdf_field='pdf_url', 
    include_bounding_box: bool=True,
    pre_show_hook=None, 
    autodelete_images=True, 
    pdf_image_size=800, stroke_color=(1, 0, 0),
    stroke_width=1, return_images=False, hide_images: bool=False):
    """
    Parameters:
        pre_show_hook: Is there a function you would like to run on each result
        before you show a PDF
    """
    to_show = []
    pdf_filepath = "temp.pdf"
    if 'results' in results:
        results = results['results']
    for i, r in enumerate(results):
        with open(pdf_filepath, 'wb') as f:
            f.write(requests.get(r[pdf_field]).content)
        if include_bounding_box:
            a = PdfAnnotator(pdf_filepath)
            bounding_box = r['bounding_box']
            points = [[coord['x'] * 72, (r['page_height'] - coord['y']) * 72] for coord in bounding_box]
            a.add_annotation(
                'polyline',
                Location(points=points, page=r['page_number'] - 1),
                Appearance(stroke_color=stroke_color, stroke_width=stroke_width),
            )
            if autodelete_images: os.remove(pdf_filepath)
            a.write(pdf_filepath)
        images = convert_from_path(pdf_filepath, size=pdf_image_size)
        # HTML(r['text_all'].replace(r['text'], '<b>' + r['text'] + '</b>').replace('\n', '<br>'))
        to_show.append(images[r['page_number'] - 1])
        if pre_show_hook is not None: pre_show_result_hook(r)
        if not hide_images: display(images[r['page_number'] - 1])
    if return_images:
        return to_show

