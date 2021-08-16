import os

def create_text_file_path(package_dir, ticker, source):
    source_name = get_source_name(source)
    file = f"{source_name}.txt"
    text_file_path = f"{package_dir}/text/{ticker}/{file}"
    ticker_path = f"{package_dir}/text/{ticker}"
    if not os.path.exists(ticker_path):
        os.makedirs(ticker_path, exist_ok = True)
    return text_file_path

def create_png_file_path(package_dir, ticker, source):
    source_name = get_source_name(source)
    file = f"{source_name}.png"
    text_file_path = f"{package_dir}/maps/{ticker}/{file}"
    ticker_path = f"{package_dir}/maps/{ticker}"
    if not os.path.exists(ticker_path):
        os.makedirs(ticker_path, exist_ok = True)
    return text_file_path

def create_pdf_file_path(package_dir, ticker, source):
    source_name = get_source_name(source)
    file = f"{source_name}.pdf"
    text_file_path = f"{package_dir}/PDFs/{ticker}/{file}"
    ticker_path = f"{package_dir}/PDFs/{ticker}"
    if not os.path.exists(ticker_path,):
        os.makedirs(ticker_path, exist_ok = True)
    return text_file_path

def get_source_name(source):
    if is_website(source):
        source = "".join(source.split("/"))
        return source
    else:
        file = source.split("/")[-1]
        return file.split(".")[0]

def is_website(location):
    return len(location.split("www.")) > 1 or len(location.split("https://")) > 1