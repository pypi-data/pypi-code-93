import gdown
import tkinter as tk
import tkinter.filedialog as fd

def download():
    root = tk.Tk()
    root.overrideredirect(True)
    root.geometry('0x0+0+0')
    root.focus_force()
    path = fd.askdirectory()
    root.destroy()
    
    url = 'https://drive.google.com/u/0/uc?id=1-97yHevn9gdJ_9rLoDd_TT6HLcxkOXtn&export=download'
    filename = '/kucis_dataset.7z'
    gdown.download(url, path + filename, quiet=False)
