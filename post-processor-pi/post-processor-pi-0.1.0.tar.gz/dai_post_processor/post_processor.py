import os
import json
import base64
import re
import statistics
from collections import OrderedDict
from matplotlib.widgets import RectangleSelector
import matplotlib.image as mpimg
import matplotlib.pyplot as plt
from tkinter import *
from tkinter import ttk
from tkinter import messagebox
import base64


class DocumentClass:
    def __init__(self, doc_ai, config_dict):
        # Document AI output
        self.doc_ai = doc_ai

        # Configuration file
        self.paragraph_multiplier = config_dict["paragraph_multiplier"]
        self.header_multiplier = config_dict["header_multiplier"]
        self.line_threshold = config_dict["line_threshold"]
        self.line_repeat = config_dict["line_repeat"]
        self.thr_left = config_dict["thr_left"]
        self.thr_right = config_dict["thr_right"]
        self.thr_top = config_dict["thr_top"]
        self.thr_bottom = config_dict["thr_bottom"]
        self.main_filter = config_dict["main_filter"]
        self.lines_output = config_dict["lines_output"]
        self.paragraph_output = config_dict["paragraph_output"]
        self.structured_output = config_dict["structured_output"]
        self.headers_output = config_dict["headers_output"]
        self.get_nested_filter_1 = config_dict["get_nested_filter_1"]
        if self.get_nested_filter_1:
            self.nested_filter_1 = config_dict["nested_filter_1"]

    def create_json(self, file_name="test"):

        def create_lines_features():

            thr_left = self.thr_left
            thr_right = self.thr_right
            thr_top = self.thr_top
            thr_bottom = self.thr_bottom

            row_list = []
            for json_file in self.doc_ai:

                for page in json_file["pages"]:

                    width = page["image"]["width"]

                    try:
                        page_list = []
                        for paragraph in page["lines"]:

                            try:
                                y_top = paragraph["layout"]["boundingPoly"]["vertices"][0]["y"]
                                x_left = paragraph["layout"]["boundingPoly"]["vertices"][0]["x"]
                                y_bottom = paragraph["layout"]["boundingPoly"]["vertices"][2]["y"]
                                x_right = paragraph["layout"]["boundingPoly"]["vertices"][2]["x"]

                                if (y_top > thr_top) and (x_left > thr_left) and (y_bottom < thr_bottom) and (
                                        x_right < thr_right):

                                    response = ""
                                    features_dict = {}
                                    row = {}
                                    row["line_features"] = features_dict
                                    for segment in paragraph["layout"]["textAnchor"]["textSegments"]:
                                        try:
                                            int(segment["startIndex"])
                                        except KeyError:
                                            start_index = 0
                                        else:
                                            start_index = int(segment["startIndex"])
                                        end_index = int(segment["endIndex"])

                                        response += json_file["text"][start_index:end_index]

                                        response = response.replace("\n", " ")
                                        response = response.strip()

                                        features_dict["y_top"] = paragraph["layout"]["boundingPoly"]["vertices"][0]["y"]
                                        features_dict["x_left"] = paragraph["layout"]["boundingPoly"]["vertices"][0]["x"]
                                        features_dict["y_bottom"] = paragraph["layout"]["boundingPoly"]["vertices"][2]["y"]
                                        features_dict["x_right"] = paragraph["layout"]["boundingPoly"]["vertices"][2]["x"]
                                        row["text"] = response
                                        features_dict["page_num"] = page["pageNumber"]
                                        page_list.append(row)
                            except:
                                pass

                    except:
                        pass

                    row_list.append(page_list)

            for j in range(self.line_repeat):

                for page in row_list:

                    for i in range(len(page)):
                        try:
                            if abs(page[i]["line_features"]["y_top"] - page[i + 1]["line_features"]["y_top"]) < self.line_threshold:
                                page[i]["text"] = page[i]["text"] + " " + page[i + 1]["text"]
                                page[i]["line_features"]["x_right"] = page[i + 1]["line_features"]["x_right"]
                                del page[i + 1]
                        except:
                            pass

            for page in row_list:

                for i in range(len(page)):

                    try:
                        page[i]["line_features"]["gap_left"] = page[i + 1]["line_features"]["x_left"] - page[i]["line_features"]["x_left"]
                        page[i]["line_features"]["gap_right"] = page[i]["line_features"]["x_right"] - page[i + 1]["line_features"]["x_right"]
                        page[i]["line_features"]["gap_horizontal"] = page[i]["line_features"]["gap_left"] + page[i]["line_features"]["gap_right"]
                    except:
                        pass

                    try:
                        page[i]["line_features"]["gap_top"] = abs(page[i]["line_features"]["y_top"] - page[i - 1]["line_features"]["y_bottom"])
                    except:
                        pass

                    page[i]["line_features"]["gap_right_page"] = width - page[i]["line_features"]["x_right"]
                    page[i]["line_features"]["gap_page"] = page[i]["line_features"]["gap_right_page"] + page[i]["line_features"]["x_left"]
                try:
                    page[0]["line_features"]["gap_top"] = page[0]["line_features"]["y_top"]
                except:
                    page[0]["line_features"]["gap_top"] = 0

                page[0]["line_features"]["gap_left"] = 0
                page[0]["line_features"]["gap_right"] = 0
                page[0]["line_features"]["gap_horizontal"] = 0

            if self.headers_output:
                gap = []
                for page in row_list:
                    for row in page:
                        gap.append(row["line_features"]["gap_page"])

                header_thr = statistics.median(gap) * self.header_multiplier

                for page in row_list:
                    for i in range(len(page)):
                        if page[i]["line_features"]["gap_page"] > header_thr and (page[i]["line_features"]["x_left"] - 0.05 * page[i]["line_features"]["x_left"]) < \
                                page[i]["line_features"]["gap_right_page"] < (page[i]["line_features"]["x_left"] + 0.05 * page[i]["line_features"]["x_left"]):
                            page[i]["type"] = "centered header"
                        else:
                            page[i]["type"] = "line"

            return row_list

        def filter_paragraphs(row_list):

            i = 0
            cor = []
            id = []
            for page in row_list:
                for line in page:
                    if line["line_features"]["gap_top"] is not None:
                        cor.append(line["line_features"]["gap_top"])
                        id.append(i)
                        i += 1

            median = statistics.median(cor)
            gap_threshold = median * self.paragraph_multiplier

            paragraph_list = []
            for page in row_list:

                for i in range(len(page)):
                    page[i]["id"] = i

                page_iter = iter(page)
                for line in page_iter:
                    l = line["id"]
                    par_features_dict = {}
                    paragraph_dict = {}
                    paragraph_dict["par_features"] = par_features_dict
                    paragraph_text = ""
                    gap = 0
                    i = 0
                    while gap < gap_threshold and i < len(page) - 2:
                        try:
                            if self.headers_output == 1:
                                if page[l + i]["type"] == "line":
                                    paragraph_text += " " + page[l + i]["text"]

                                    gap = page[l + i + 1]["line_features"]["gap_top"]
                            else:

                                paragraph_text += " " + page[l + i]["text"]

                                gap = page[l + i + 1]["line_features"]["gap_top"]
                        except:
                            pass

                        i += 1
                    paragraph_dict["text"] = paragraph_text.strip()
                    paragraph_dict["par_features"]["page_num"] = page[0]["line_features"]["page_num"]
                    paragraph_dict["par_features"]["gap_top"] = page[l]["line_features"]["gap_top"]
                    paragraph_dict["par_features"]["x_left"] = page[l]["line_features"]["x_left"]
                    paragraph_dict["par_features"]["x_right"] = page[l]["line_features"]["x_right"]
                    paragraph_dict["par_features"]["y_top"] = page[l]["line_features"]["y_top"]
                    paragraph_list.append(paragraph_dict)
                    try:
                        [next(page_iter) for j in range(i - 1)]
                    except:
                        pass
            for i in range(1, len(paragraph_list)):
                y_top_previous = paragraph_list[i - 1]["par_features"]["y_top"]
                y_top_current = paragraph_list[i]["par_features"]["y_top"]
                if y_top_current < y_top_previous:
                    paragraph_list[i]["par_features"]["gap_left"] = 0
                    paragraph_list[i]["par_features"]["gap_right"] = 0
                else:
                    paragraph_list[i]["par_features"]["gap_left"] = paragraph_list[i - 1]["par_features"]["x_left"] - paragraph_list[i]["par_features"]["x_left"]
                    paragraph_list[i]["par_features"]["gap_right"] = paragraph_list[i]["par_features"]["x_right"] - paragraph_list[i - 1]["par_features"]["x_right"]

            paragraph_list[0]["par_features"]["gap_left"] = 0
            paragraph_list[0]["par_features"]["gap_right"] = 0

            return paragraph_list

        def nested_strcuture_1(paragraph_list):
            nested_output_pattern1 = re.findall(self.nested_filter_1, self.doc_ai[0]["text"])
            nested_output_pattern1 = [out for out in nested_output_pattern1 if
                                      len(out.replace("(", "").replace(")", "")) == 1]

            for i in range(len(paragraph_list)):
                paragraph_list[i]["id"] = i

            paragraph_iter = iter(paragraph_list)
            paragraph_list_new = []
            for paragraph in paragraph_iter:
                l = paragraph["id"]
                paragraph["nested_structure_1"] = []
                i = 0
                while any(string in paragraph_list[l + i]["text"][:10] for string in nested_output_pattern1):
                    if i != 0:
                        paragraph["text"] += " " + paragraph_list[l + i]["text"]
                    section_letter = re.findall(self.nested_filter_1, paragraph_list[l + i]["text"][:10])[0]
                    nested_structure = {}
                    nested_structure.update(
                        {"name": "section_{}".format(section_letter),
                         "text": "{}".format(paragraph_list[l + i]["text"])})
                    paragraph["nested_structure_1"].append(nested_structure)

                    i += 1

                paragraph_list_new.append(paragraph)

                try:
                    [next(paragraph_iter) for j in range(i - 1)]
                except:
                    pass

            return paragraph_list_new

        def structure_paragraphs(paragraph_list, output_pattern):
            for i in range(len(paragraph_list)):
                paragraph_list[i]["id"] = i

            paragraph_iter = iter(paragraph_list)
            structured_paragraph_list = []
            for paragraph in paragraph_iter:
                nested_paragraph_list_1 = []
                text = ""
                if any(string in paragraph["text"][:10] for string in output_pattern):
                    l = paragraph["id"]
                    paragraph_text = ""

                    i = 0
                    while not any(string in text[:10] for string in output_pattern):

                        try:
                            paragraph_text += " " + paragraph_list[l + i]["text"]
                            text = paragraph_list[l + i + 1]["text"]
                            if len(paragraph_list[l + i]["nested_structure_1"]) > 0:
                                nested_paragraph_list_1 = paragraph_list[l + i]["nested_structure_1"]
                        except:
                            break

                        i += 1

                    paragraph_dict = {
                        "paragraph_number": [ele for ele in output_pattern if (ele in paragraph_text[:10])][0],
                        "text": paragraph_text.strip(), "nested_structure_1": nested_paragraph_list_1
                    }

                    structured_paragraph_list.append(paragraph_dict)

            return structured_paragraph_list

        def filtering_function():
            match = []
            for json_file in self.doc_ai:
                match += re.findall(self.main_filter, json_file["text"].replace("\n", " "))

                match = OrderedDict((x, True) for x in match).keys()
                match = list(match)

            match = [x[:-1].strip() for x in match]

            output_pattern = []
            for element in match:
                if element not in output_pattern:
                    output_pattern.append(element)

            return output_pattern

        output_pattern = filtering_function()

        row_list = create_lines_features()

        paragraph_list = filter_paragraphs(row_list)

        if self.get_nested_filter_1:
            paragraph_list = nested_strcuture_1(paragraph_list)

        structure_paragraphs_list = structure_paragraphs(paragraph_list, output_pattern)

        output_dict = {}
        if self.lines_output == 1:
            output_dict["lines_list"] = row_list
        if self.paragraph_output == 1:
            output_dict["paragraph_list"] = paragraph_list
        if self.structured_output == 1:
            output_dict["structured_output"] = structure_paragraphs_list

        output = os.path.join("data", "pp_output", "{}.json".format(file_name))
        if not os.path.exists(os.path.dirname(output)):
            try:
                os.makedirs(os.path.dirname(output))
            except:
                pass

        with open(output, 'w') as outfile:
            print("Output JSON written to {}".format(outfile.name))
            json.dump(output_dict, outfile, ensure_ascii=False)

        return output_dict


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

            img = mpimg.imread("data/various/gui_input/gui_page.png")
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


def open_doc_ai(path, return_title=False):

    def atoi(text):
        return int(text) if text.isdigit() else text

    def natural_keys(text):
        return [atoi(c) for c in re.split(r'(\d+)', text)]

    file_list = os.listdir(path)
    title = file_list[0][24:-7]

    sort_list = sorted(file_list, key=natural_keys)

    doc_ai = []
    for file in sort_list:

        # If file is a json, construct it's full path and open it, append all json data to list
        if 'json' in file:
            json_path = os.path.join(path, file)
            with open(json_path) as json_file:
                data = json.load(json_file)
            doc_ai.append(data)

    if return_title:
        output = (doc_ai, title)
    else:
        output = doc_ai

    return output


def atoi(text):
    return int(text) if text.isdigit() else text


def natural_keys(text):
    '''
    alist.sort(key=natural_keys) sorts in human order
    http://nedbatchelder.com/blog/200712/human_sorting.html
    (See Toothy's implementation in the comments)
    '''
    return [atoi(c) for c in re.split(r'(\d+)', text)]