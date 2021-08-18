"""
Custom widgets for the bookfolder UI.
"""

import tkinter
from tkinter import filedialog
from tkinter import messagebox
from tkinter import ttk
from tkinter import N, E, S, W

from bookfolder.pattern_creator import PatternCreator


class WidgetFrame():
    """
    Superclass for widgets within the window.
    """

    x_padding = "4p"
    y_padding = "2p"
    frame_sticky = (N, E, S, W)

    def add_to_grid(self, component, column=0, row=0, padx=None, pady=None,
                    **kwargs):
        """
        Add given `component` to a grid layout.
        """
        # pylint: disable=too-many-arguments

        if padx is None:
            padx = self.x_padding
        if pady is None:
            pady = self.y_padding

        component.grid(column=column, row=row, padx=padx, pady=pady, **kwargs)


class HorizontalSeparator(WidgetFrame):
    """
    Frame containing a horizontal separator
    """

    y_padding = "5p"

    def __init__(self, parent_window):
        self._frame = ttk.Frame(parent_window)
        self._frame.grid(column=0, row=0, sticky=self.frame_sticky)

    @property
    def frame(self):
        """
        Generate the frame and the field within
        """
        separator = ttk.Separator(self._frame, orient="horizontal")
        self.add_to_grid(separator, column=0, row=0, sticky=(E, W))
        self._frame.columnconfigure(0, weight=1)
        return self._frame


class CustomizationOptionTextInputFrame(WidgetFrame):
    """
    Superclass for customization options set via a text input frame
    """
    frame_sticky = (N, E, S)
    field_width = 5


class MeasurementIntervalFrame(CustomizationOptionTextInputFrame):
    """
    Return a Frame with text box for entering page number
    """

    def __init__(self, parent_window):
        self._frame = ttk.Frame(parent_window)
        self._frame.grid(column=0, row=0, sticky=self.frame_sticky)
        self.measurement_interval = tkinter.DoubleVar(value=0.25)

    @property
    def frame(self):
        """
        Generate the frame and the field within
        """
        label = tkinter.Label(
            self._frame,
            text="Height of one pixel in mm")
        self.add_to_grid(label, column=0, row=0, sticky=(E))

        measurement_interval_entry = ttk.Entry(
                self._frame,
                textvariable=self.measurement_interval,
                width=self.field_width,
                )
        self.add_to_grid(measurement_interval_entry,
                         column=1, row=0, sticky=(E))

        return self._frame


class PageNumberFrame(CustomizationOptionTextInputFrame):
    """
    Return a Frame with text box for entering page number
    """

    def __init__(self, parent_window):
        self._frame = ttk.Frame(parent_window)
        self._frame.grid(column=0, row=0, sticky=self.frame_sticky)
        self.first_page_number = tkinter.IntVar(value=1)

    @property
    def frame(self):
        """
        Generate the frame and the field within
        """
        label = tkinter.Label(
            self._frame,
            text="Page number of first pattern sheet in the pattern")
        label.grid(column=0, row=0, sticky=(E))

        page_number_entry = ttk.Entry(
                self._frame,
                textvariable=self.first_page_number,
                width=self.field_width,
                )
        self.add_to_grid(page_number_entry,
                         column=1, row=0, sticky=(W))

        return self._frame


class GeneratePatternFrame(WidgetFrame):
    """
    Return a Frame with button to generate the pattern.
    """

    y_padding = ("10p", "3p")

    def __init__(self, parent_window, input_path, output_path,
                 measurement_interval, start_page):
        # pylint: disable=too-many-arguments
        self._frame = ttk.Frame(parent_window)
        self._frame.grid(column=0, row=0, sticky=self.frame_sticky)

        self.input_path = input_path
        self.output_path = output_path
        self.measurement_interval = measurement_interval
        self.start_page = start_page

    @property
    def frame(self):
        """
        Create the Frame and the button within.
        """
        btn = ttk.Button(self._frame, text="Generate",
                         command=self._generate)
        self.add_to_grid(btn, column=1, row=0, sticky=(E))
        self._frame.columnconfigure(0, weight=1)

        return self._frame

    def _generate(self):
        """
        Generate the PDF pattern and confirm creation to the user.
        """
        pattern_creator = PatternCreator(self.input_path.get(),
                                         self.measurement_interval.get(),
                                         self.start_page.get())
        pattern_creator.save_pdf(self.output_path.get())

        messagebox.showinfo(
            "Success",
            "Wrote the pattern to {}".format(self.output_path.get()))


class FileIOFrame(WidgetFrame):
    """
    Create a frame for selecting a file for input/output.
    """

    label_text = ""
    button_text = "Browse"

    def __init__(self, parent_window):
        self._frame = ttk.Frame(parent_window)
        self._frame.grid(column=0, row=0, sticky=self.frame_sticky)

        self.path = tkinter.StringVar()

    @property
    def frame(self):
        """
        Create the Frame and its components.

        :returns: the created Frame
        """

        label = tkinter.Label(self._frame, text=self.label_text, anchor=E)
        self.add_to_grid(label, column=0, row=0, sticky=(W, E))
        self._frame.columnconfigure(0, minsize="100p")

        image_textbox = ttk.Entry(self._frame, textvariable=self.path)
        self.add_to_grid(image_textbox, column=1, row=0, sticky=(E, W))

        btn_browse = ttk.Button(self._frame, text=self.button_text,
                                command=self._browse_files)
        self.add_to_grid(btn_browse, column=2, row=0, sticky=(W))

        self._frame.columnconfigure(1, weight=1)

        return self._frame

    def _browse_files(self):
        raise NotImplementedError("Must be implemented in subclasses")


class ImageInput(FileIOFrame):
    """
    Create a Frame for selecting source image for the pattern
    """

    label_text = "Source image"

    def _browse_files(self):
        filename = filedialog.askopenfilename(
            title="Select a File",
            filetypes=(
                ("Image files", "*.png"),
                ("all files", "*.*"),
                ),
            )

        self.path.set(filename)


class PDFOutput(FileIOFrame):
    """
    Create a Frame for selecting PDF output location
    """

    label_text = "Save as"

    def _browse_files(self):
        filename = filedialog.asksaveasfilename(
            title="Save as",
            filetypes=(
                ("PDF files", "*.pdf"),
                ("all files", "*.*"),
                ),
            )

        self.path.set(filename)
