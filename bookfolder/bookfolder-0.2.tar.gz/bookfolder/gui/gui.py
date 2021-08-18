"""
Graphical user interface for bookfolder
"""

import tkinter
from tkinter import N, E, S, W

from bookfolder.gui.widgets import (
    HorizontalSeparator,
    MeasurementIntervalFrame,
    PageNumberFrame,
    GeneratePatternFrame,
    ImageInput,
    PDFOutput,
    )


class GUI():
    """
    Graphical user interface for bookfolder
    """

    def __init__(self):
        self.image_path = ""

    def show(self):
        """
        Show the GUI to the user
        """
        window = tkinter.Tk()
        window.title("Bookfolding Pattern Creator")
        window.grid_columnconfigure(0, weight=1)

        outer_frame = tkinter.Frame()
        outer_frame.grid(padx="8p", pady="8p", sticky=(N, E, S, W))
        outer_frame.grid_columnconfigure(0, weight=1)

        image_input = ImageInput(outer_frame)
        pdf_output = PDFOutput(outer_frame)
        separator = HorizontalSeparator(outer_frame)
        measurement_interval_input = MeasurementIntervalFrame(outer_frame)
        page_number_input = PageNumberFrame(outer_frame)

        generate = GeneratePatternFrame(
            outer_frame,
            image_input.path,
            pdf_output.path,
            measurement_interval_input.measurement_interval,
            start_page=page_number_input.first_page_number
            )

        self._add_components_vertically(
            [
                image_input.frame,
                pdf_output.frame,
                separator.frame,
                measurement_interval_input.frame,
                page_number_input.frame,
                generate.frame,
            ])

        window.mainloop()

    def _add_components_vertically(self, components):
        """
        Add given `components` to a grid on top of each other.
        """
        # pylint: disable=no-self-use
        for index, component in enumerate(components):
            component.grid(row=index, column=0)
