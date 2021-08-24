import io

import PyPDF2
from pdf2image import convert_from_bytes

import signer_pdf.sign_generator as sign_generator


def sign(name, date, a_hash, position, in_file):
    original = PyPDF2.PdfFileReader(in_file, strict=False)
    first_page = original.getPage(0)

    pdf_with_signed_page = PyPDF2.PdfFileWriter()
    pdf_with_signed_page.addPage(first_page)
    pdf_with_signed_page_bytes = io.BytesIO()
    pdf_with_signed_page.write(pdf_with_signed_page_bytes)
    pdf_with_signed_page_bytes.seek(0)

    images = convert_from_bytes(pdf_with_signed_page_bytes.read())

    signed_page_bytes = sign_generator.convert(name, date, a_hash, position, images[0])
    signed_page = PyPDF2.PdfFileReader(signed_page_bytes).getPage(0)

    media_3 = float(first_page['/MediaBox'][3])
    if first_page.get('/Rotate', 0) in [90, 270]:
        signed_page.scaleTo(float(first_page['/MediaBox'][3]), float(first_page['/MediaBox'][2]))
    else:
        signed_page.scaleTo(float(first_page['/MediaBox'][2]), media_3 if media_3 > 0 else float(first_page['/MediaBox'][1]))

    output_signed_pdf = PyPDF2.PdfFileWriter()
    for i in range(original.getNumPages()):
        if i == 0:
            output_signed_pdf.addPage(signed_page)
        else:
            page = original.getPage(i)
            output_signed_pdf.addPage(page)

    fp = io.BytesIO()
    output_signed_pdf.write(fp)
    return fp
