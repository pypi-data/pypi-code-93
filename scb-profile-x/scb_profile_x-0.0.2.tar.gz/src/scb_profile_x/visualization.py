from typing import List, Union

from PIL import Image, ImageDraw, ImageFont
from IPython.display import display
import matplotlib.pyplot as plt
import math
import os

TEMPLATE_IMG_PATH = os.path.join(os.path.dirname(__file__), "profile_x_template_v3_18_rows.png")
PROMPT_REGULAR_PATH = os.path.join(os.path.dirname(__file__), "Prompt-Regular.ttf")
PROMPT_SEMIBOLD_PATH = os.path.join(os.path.dirname(__file__), "Prompt-SemiBold.ttf")
PROMPT_LIGHT_PATH = os.path.join(os.path.dirname(__file__), "Prompt-Light.ttf")
PROMPT_MEDIUM_PATH = os.path.join(os.path.dirname(__file__), "Prompt-Medium.ttf")
IS_SINGLE_TARGET = False
MY_MONITOR_DPI = 96

FONT_MULTIPLY_FACTOR = 14
HEADER_FONT = ImageFont.truetype(PROMPT_SEMIBOLD_PATH, 5 * FONT_MULTIPLY_FACTOR)
LABEL_FONT = ImageFont.truetype(PROMPT_MEDIUM_PATH, 6 * FONT_MULTIPLY_FACTOR)
DATE_FONT = ImageFont.truetype(PROMPT_MEDIUM_PATH, 4 * FONT_MULTIPLY_FACTOR)
GUIDELINE_FONT = ImageFont.truetype(PROMPT_MEDIUM_PATH, 4 * FONT_MULTIPLY_FACTOR)
GUIDELINE_FONT_ST = ImageFont.truetype(PROMPT_MEDIUM_PATH, round(3.5 * FONT_MULTIPLY_FACTOR) - 1)
CATEGORY_HEADER_FONT = ImageFont.truetype(PROMPT_SEMIBOLD_PATH, 6 * FONT_MULTIPLY_FACTOR)
CATEGORY_FONT = ImageFont.truetype(PROMPT_MEDIUM_PATH, 5 * FONT_MULTIPLY_FACTOR)
DEVIATION_FONT = ImageFont.truetype(PROMPT_SEMIBOLD_PATH, 4 * FONT_MULTIPLY_FACTOR)


def _get_text_size(text, font) -> int:
    im = Image.new('L', (64, 64), 0xFF)
    draw = ImageDraw.Draw(im)
    im.close()
    return draw.textsize(text, font)


HEADER_TEXTS = ("Percent", "No of custs", "Percent", "Deviation", "No of custs", "Percent", "Deviation")
LABEL_TEXTS = ("Total SCB Customer", "Target 1", "Target 2")
NUMBER_TEXTS = ("Total Cust: XX.X M", "Total Cust: XX.X M", "Total Cust: XX.X M")
DATE_TEXTS = ("as of Xxx 21", "as of Xxx 21", "as of Xxx 21")
GUIDELINE_TEXT = "Guideline: If the deviation from Total SCB Customer > 0, it means our target customers are skewing towards that profile"
DATA_AS_ROWS = [["Age"],
                ["Under 20", "5 %", "X,XXX", "2 %", -3, "X,XXX", "2 %", -3],
                ["20 - 30", "26 %", "XX,XXX", "35 %", 9, "XX,XXX", "35 %", 9],
                ["30 - 40", "24 %", "XX,XXX", "36 %", 12, "XX,XXX", "36 %", 12],
                ["40 - 50", "21 %", "XX,XXX", "19 %", -4, "XX,XXX", "19 %", -4],
                ["Above 50", "24 %", "XX,XXX", "8 %", -12, "XX,XXX", "8 %", -12],
                ["Gender"],
                ["Male", "5 %", "X,XXX", "2 %", 9, "X,XXX", "2 %", 12],
                ["Female", "26 %", "XX,XXX", "35 %", 9, "XX,XXX", "35 %", 9],
                ["Segment"],
                ["Private", "5 %", "X,XXX", "2 %", -3, "X,XXX", "2 %", -3],
                ["First", "26 %", "XX,XXX", "35 %", 9, "X,XXX", "35 %", 9],
                ["Prime", "24 %", "XX,XXX", "36 %", 12, "X,XXX", "36 %", 12],
                ["Wealth Potential", "21 %", "XX,XXX", "19 %", -4, "X,XXX", "19 %", -4],
                ["Upper Mass", "24 %", "XX,XXX", "8 %", 99, "XX,XXX", "8 %", -35]]


def _rescale_box_sd(value: int) -> int:
    if abs(value) <= 25:
        return_value = abs(value)
    else:
        return_value = math.log(abs(value)) * 7.38 + 1
    if value < 0:
        return_value = - return_value
    return return_value


def display_img(img: Image):
    plt.figure(figsize=(img.size[0] / MY_MONITOR_DPI, img.size[1] / MY_MONITOR_DPI))
    plt.imshow(img)
    plt.axis('off')
    display(plt.show())


def split_rows_into_pages(data_as_rows: List[List[Union[str, int]]], no_of_row_per_page: int = 18) -> List[List[List[Union[str, int]]]]:
    # define header position
    header_positions = []
    for i in range(len(data_as_rows)):
        if len(data_as_rows[i]) == 1:
            header_positions += [i]
    header_positions += [len(data_as_rows)]

    # put data into pages
    current_no_of_empty_rows = 0
    data_as_pages = []
    for i in range(len(header_positions) - 1):
        content_length = header_positions[i + 1] - header_positions[i]
        if current_no_of_empty_rows < content_length:
            data_as_pages += [[]]
            current_no_of_empty_rows = no_of_row_per_page
        data_as_pages[-1] += data_as_rows[header_positions[i]:header_positions[i + 1]]
        current_no_of_empty_rows -= content_length

    return data_as_pages


def generate_graphic(data_as_rows: List[List[Union[str, int]]] = (), header_texts: List[str] = HEADER_TEXTS, label_texts: List[str] = LABEL_TEXTS,
                     number_texts: List[str] = NUMBER_TEXTS, date_texts: List[str] = DATE_TEXTS, guideline_text: str = GUIDELINE_TEXT) -> Image:
    with Image.open(TEMPLATE_IMG_PATH) as img:
        W, H = img.size
        # print(f"Template size = {W}, {H}")
        canvas = ImageDraw.Draw(img)

        # Header plot
        header_x_pos_list = [1388, 2104, 2578, 3144, 3922, 4384, 4940]
        for header_x_pos, header_text in zip(header_x_pos_list, header_texts):
            canvas.text((header_x_pos, 580), header_text, font=HEADER_FONT, fill="#4e2a82", anchor="rs")

        # Label plot
        box_x_width_list = [1328, 1686, 1686]
        box_x_pos_list = [154, 1592, 3402]

        for box_x_width, box_x_pos, label_text in zip(box_x_width_list, box_x_pos_list, label_texts):
            text_size = _get_text_size(label_text, LABEL_FONT)
            label_x_pos = box_x_pos + (box_x_width - text_size[0]) / 2
            canvas.text((label_x_pos, 328), label_text, font=LABEL_FONT, fill="#ffffff", anchor="ls")

        # Number plot
        number_x_pos_list = [203, 1653, 3456]
        for number_x_pos, number_text in zip(number_x_pos_list, number_texts):
            canvas.text((number_x_pos, 436), number_text, font=DATE_FONT, fill="#ffffff", anchor="ls")

        # Date plot
        date_x_pos_list = [1102, 2900, 4700]
        for date_x_pos, date_text in zip(date_x_pos_list, date_texts):
            canvas.text((date_x_pos, 436), date_text, font=DATE_FONT, fill="#ffffff", anchor="ls")

        # Guideline plot
        if IS_SINGLE_TARGET:
            canvas.text((3040, H - 144), guideline_text, font=GUIDELINE_FONT_ST, fill="#4e2a82", anchor="rs")
        else:
            canvas.text((4755, H - 133), guideline_text, font=GUIDELINE_FONT, fill="#4e2a82", anchor="rs")

        # row plot
        for i, row in enumerate(data_as_rows):
            # Deviation baseline
            if i > 0:
                canvas.line((2976, 692 + 116 * (i - 1), 2976, 692 + 116 * i), fill="#000000", width=4)  # deviation line for target 1
                canvas.line((4786, 692 + 116 * (i - 1), 4786, 692 + 116 * i), fill="#000000", width=4)  # deviation line for target 2
            # Header
            if len(row) == 1:
                canvas.text((918, 666 + 116 * i), row[0], font=CATEGORY_HEADER_FONT, fill="#4e2a82", anchor="rs")
            # Data row
            elif len(row) == 8:
                if type(row[4]) != int or type(row[7]) != int:
                    raise Exception("Expect row[4] and row[7] as integer (deviation)")
                canvas.text((918, 666 + 116 * i), row[0], font=CATEGORY_FONT, fill="#4e2a82", anchor="rs")  # "Under 20"
                canvas.text((1388, 666 + 116 * i), row[1], font=CATEGORY_FONT, fill="#4e2a82", anchor="rs")  # "5 %"
                canvas.text((2104, 666 + 116 * i), row[2], font=CATEGORY_FONT, fill="#4e2a82", anchor="rs")  # "4,295"
                canvas.text((2578, 666 + 116 * i), row[3], font=CATEGORY_FONT, fill="#4e2a82", anchor="rs")  # 2 %

                box_multiply_factor = 8
                if row[4] < 0:
                    box_color = "#eb4d3d"
                    text_offset = -24
                    text_anchor = "rs"
                else:
                    box_color = "#aad73e"
                    text_offset = 24
                    text_anchor = "ls"
                canvas.rectangle((2978 + (_rescale_box_sd(row[4]) * box_multiply_factor), 692 + 116 * (i - 1), 2978, 692 + 116 * (i) + 4), fill=box_color,
                                 outline="#000000", width=4)  # deviation box
                canvas.text((2978 + (_rescale_box_sd(row[4]) * box_multiply_factor) + text_offset, 692 + 116 * (i) - 40), str(row[4]), font=DEVIATION_FONT,
                            fill='#4e2a82', anchor=text_anchor)  # deviation text

                canvas.text((3922, 666 + 116 * i), row[5], font=CATEGORY_FONT, fill="#4e2a82", anchor="rs")  # "4,295"
                canvas.text((4390, 666 + 116 * i), row[6], font=CATEGORY_FONT, fill="#4e2a82", anchor="rs")  # 2 %

                if row[7] < 0:
                    box_color = "#eb4d3d"
                    text_offset = -24
                    text_anchor = "rs"
                else:
                    box_color = "#aad73e"
                    text_offset = 24
                    text_anchor = "ls"
                canvas.rectangle((4788 + (_rescale_box_sd(row[7]) * box_multiply_factor), 692 + 116 * (i - 1), 4788, 692 + 116 * (i) + 4), fill=box_color,
                                 outline="#000000", width=4)  # deviation box
                canvas.text((4788 + (_rescale_box_sd(row[7]) * box_multiply_factor) + text_offset, 692 + 116 * (i) - 40), str(row[7]), font=DEVIATION_FONT,
                            fill='#4e2a82', anchor=text_anchor)  # deviation text
            else:
                raise Exception(f"Expect  8 fields in a row, got [{len(row)}] fields")
    return img


def generate_example_graphic() -> Image:
    return generate_graphic(data_as_rows=DATA_AS_ROWS)
