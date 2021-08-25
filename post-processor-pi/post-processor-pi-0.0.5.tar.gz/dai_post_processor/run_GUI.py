from dai_post_processor import post_processor as pp
from matplotlib.widgets import RectangleSelector
import matplotlib.pyplot as plt
from tkinter import *
from tkinter import ttk
from tkinter import messagebox
import argparse
import base64
import json
import cv2
import os


class configGUI:
    def __init__(self, doc_ai):

        self.doc_ai = doc_ai
        image = self.doc_ai[0]["pages"][0]["image"]
        self.thr_left = 0
        self.thr_right = image["width"]
        self.thr_top = 0
        self.thr_bottom = image["height"]
        self.get_nested_filter_1 = False
        self.toggle_selector = None

        # Defining Window
        self.win = Tk()
        self.win.title("Configuration GUI")
        self.win.geometry("400x500+10+10")

        top = Frame(self.win)
        bottom = Frame(self.win)
        top.pack(side=TOP)
        bottom.pack(side=BOTTOM)

        # Create tabs
        tab_control = ttk.Notebook(self.win)
        tab1 = ttk.Frame(tab_control, style="TFrame")
        tab2 = ttk.Frame(tab_control)
        tab_control.add(tab1, text='Main')
        tab_control.add(tab2, text='Advanced')
        tab_control.pack(expand=1, fill="both")

        # Main tab

        tab1.grid_rowconfigure(0, weight=1)
        tab1.grid_columnconfigure(0, weight=1)
        tab1.grid_rowconfigure(1, weight=1)
        tab1.grid_rowconfigure(2, weight=1)

        # Frame 1

        self.frame1 = Frame(tab1, highlightbackground="black", highlightthickness=1)
        self.frame1.grid(row=0, column=0, sticky="nsew")

        # Entries text
        self.fr1_lbl1 = ttk.Label(self.frame1, text='Select text of interest')
        self.fr1_lbl1.place(x=0, y=0)
        self.fr1_lbl2 = Label(self.frame1, text='Page number')
        self.fr1_lbl2.place(x=10, y=65)

        # Defining Entries
        cb_list = [i + 1 for i in range(len(self.doc_ai[0]["pages"]))]
        self.page_num = ttk.Combobox(self.frame1, values=cb_list, width=5)
        self.page_num.place(x=150, y=65)

        # Frame 2

        self.frame2 = Frame(tab1, highlightbackground="black", highlightthickness=1)
        self.frame2.grid(row=1, column=0, sticky="nsew")

        # Entries text
        self.fr1_lbl2 = ttk.Label(self.frame2, text='Structuring Filter')
        self.fr1_lbl2.place(x=0, y=0)
        self.fr1_lbl2 = Label(self.frame2, text='Main structure')
        self.fr1_lbl2.place(x=10, y=30)
        self.fr1_lbl3 = Label(self.frame2, text='Nested structure 1')

        # Defining Entries
        self.main_filter = Entry(self.frame2, width=20)
        self.main_filter.place(x=150, y=30)
        self.nested_filter_1 = Entry(self.frame2, width=20)

        # Entries default values
        self.main_filter.insert(END, '([0-9]+[.]+[0-1]+[0-9]+[.]+)')
        self.nested_filter_1.insert(END, '\([a-z]\)')

        # Frame 3

        self.frame3 = Frame(tab1, highlightbackground="black", highlightthickness=1)
        self.frame3.grid(row=2, column=0, sticky="nsew")
        self.fr1_lbl2 = ttk.Label(self.frame3, text='Output')
        self.fr1_lbl2.place(x=0, y=0)

        # Check Buttons
        self.v1 = IntVar()
        self.v2 = IntVar()
        self.v3 = IntVar()
        self.v4 = IntVar()
        self.v1.set(1)
        self.v2.set(1)
        self.v3.set(1)
        self.r1 = Checkbutton(self.frame3, text="lines", variable=self.v1)
        self.r2 = Checkbutton(self.frame3, text="paragraphs", variable=self.v2)
        self.r3 = Checkbutton(self.frame3, text="structured output", variable=self.v3)
        self.r4 = Checkbutton(self.frame3, text="filter headers", variable=self.v4)
        self.r1.place(x=10, y=50)
        self.r2.place(x=90, y=50)
        self.r3.place(x=200, y=50)
        self.r4.place(x=10, y=100)

        # Advanced tab

        # Entries text
        self.lbl1 = Label(tab2, text='Paragraph multiplier')
        self.lbl2 = Label(tab2, text='Header multiplier')
        self.lbl3 = Label(tab2, text='Line threshold')
        self.lbl4 = Label(tab2, text='Line repeat')

        # Placing Entries text
        self.lbl1.place(x=10, y=50)
        self.lbl2.place(x=10, y=100)
        self.lbl3.place(x=10, y=150)
        self.lbl4.place(x=10, y=200)

        # Defining Entries
        self.t1 = Entry(tab2, width=10)
        self.t2 = Entry(tab2, width=10)
        self.t3 = Entry(tab2, width=10)
        self.t4 = Entry(tab2, width=10)

        # Entries default values
        self.t1.insert(END, '2')
        self.t2.insert(END, '1.15')
        self.t3.insert(END, '10')
        self.t4.insert(END, '2')

        # Placing Entries
        self.t1.place(x=170, y=50)
        self.t2.place(x=170, y=100)
        self.t3.place(x=170, y=150)
        self.t4.place(x=170, y=200)

        # Buttons
        self.saveButton = Button(self.win, text="Save", command=self.save_output)
        self.graphButton = Button(self.frame1, text="Draw Box", command=self.select_thresholds)
        self.addFilterButton = Button(self.frame2, text="Add Filter", command=self.add_filter_widget, width=15)
        self.removeFilterButton = Button(self.frame2, text="Remove Filter", command=self.remove_filter_widget, width=15)
        self.saveButton.pack(in_=bottom, side=LEFT)
        self.graphButton.place(x=250, y=65)
        self.addFilterButton.place(x=100, y=80)

    def save_output(self):
        config_dict = {}

        if self.toggle_selector is not None:
            text_thr = self.toggle_selector.RS.extents

        num1 = float(self.t1.get())
        num2 = float(self.t2.get())
        num3 = int(self.t3.get())
        num4 = int(self.t4.get())

        config_dict["paragraph_multiplier"] = num1
        config_dict["header_multiplier"] = num2
        config_dict["line_threshold"] = num3
        config_dict["line_repeat"] = num4
        config_dict["thr_left"] = text_thr[0]
        config_dict["thr_right"] = text_thr[1]
        config_dict["thr_top"] = text_thr[2]
        config_dict["thr_bottom"] = text_thr[3]
        config_dict["main_filter"] = self.main_filter.get()
        config_dict["lines_output"] = self.v1.get()
        config_dict["paragraph_output"] = self.v2.get()
        config_dict["structured_output"] = self.v3.get()
        config_dict["headers_output"] = self.v4.get()
        config_dict["get_nested_filter_1"] = self.get_nested_filter_1
        if self.get_nested_filter_1:
            config_dict["nested_filter_1"] = self.nested_filter_1.get()

        output = os.path.join("data", "config.json")
        if not os.path.exists(os.path.dirname(output)):
            try:
                os.makedirs(os.path.dirname(output))
            except:
                pass

        with open(output, 'w') as outfile:
            print("Output JSON written to {}".format(outfile.name))
            json.dump(config_dict, outfile, ensure_ascii=False)

    def select_thresholds(self):

        def line_select_callback(eclick, erelease):
            'eclick and erelease are the press and release events'
            global x1, y1, x2, y2
            x1, y1 = eclick.xdata, eclick.ydata
            x2, y2 = erelease.xdata, erelease.ydata

        def toggle_selector(event):
            print(' Key pressed.')
            if event.key in ['Q', 'q'] and toggle_selector.RS.active:
                toggle_selector.RS.set_active(False)
            if event.key in ['A', 'a'] and not toggle_selector.RS.active:
                toggle_selector.RS.set_active(True)

        page_num = int(self.page_num.get()) if self.page_num.get().isdigit() \
            else 1000

        if page_num > len(self.doc_ai[0]["pages"]) or page_num < 1:
            messagebox.showerror("Error", "Please insert a valid page number")
        else:
            page = self.doc_ai[0]["pages"][page_num - 1]
            image = page["image"]["content"]
            filename = os.path.join("data", "various", "gui_input", "gui_page.png")
            if not os.path.exists(os.path.dirname(filename)):
                try:
                    os.makedirs(os.path.dirname(filename))
                except:
                    pass

            with open(filename, "wb") as f:
                f.write(base64.b64decode(image))

            img = cv2.imread("data/various/gui_input/gui_page.png")
            current_ax = plt.gca()
            fig = plt.gcf()
            fig.set_size_inches(10.5, 5.5)
            implot = current_ax.imshow(img)

            toggle_selector.RS = RectangleSelector(current_ax, line_select_callback,
                                                   drawtype='box', useblit=True,
                                                   button=[1, 3],  # don't use middle button
                                                   minspanx=5, minspany=5,
                                                   spancoords='pixels',
                                                   interactive=True)

            plt.connect('key_press_event', toggle_selector)
            plt.show()

            self.toggle_selector = toggle_selector

    def add_filter_widget(self):
        self.addFilterButton.place_forget()
        self.fr1_lbl3.place(x=10, y=70)
        self.nested_filter_1.place(x=150, y=70)
        self.get_nested_filter_1 = True
        self.removeFilterButton.place(x=100, y=110)

    def remove_filter_widget(self):
        self.removeFilterButton.place_forget()
        self.fr1_lbl3.place_forget()
        self.nested_filter_1.place_forget()
        self.get_nested_filter_1 = False
        self.addFilterButton.place(x=100, y=80)

    def start(self):
        self.win.mainloop()


def main():
    args = _parse_args()
    doc_ai2 = pp.open_doc_ai(args.path)

    # Start configuration GUI
    mywin = configGUI(doc_ai2)
    mywin.start()


def _parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--path", required=True)

    return parser.parse_args()
