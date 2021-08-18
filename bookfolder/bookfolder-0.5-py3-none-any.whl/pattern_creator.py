"""
Tool for extracting a bookfolding pattern from an image.
"""

from collections import namedtuple

from imageio import imread

from bookfolder.pdf import PDFWriter
from bookfolder.sheet import Sheet


InversionPoint = namedtuple("InversionPoint", "index from_color to_color")


class PatternCreator():
    """
    A tool for creating a bookfolding pattern from an image.

    The image must be black and white, with each horizontal pixel in the image
    corresponding to one sheet of paper in the book and each vertical pixel
    corresponding to one "page coordinate unit", i.e. the accuracy of the
    measurement tool used in the folding process.
    """

    def __init__(self, input_path, measurement_interval=0.25, start_page=1):
        """
        Initiate the PatternCreator.

        :input_path: Location of the input file containing the pattern image.
        :measurement_interval: Length of one page coordinate unit in
                               millimeters. Defaults to 0.25 mm.
        """
        self.input_path = input_path
        self.measurement_interval = measurement_interval
        self.start_page = start_page
        self._sheets = []

    def sheets(self):
        """
        Return `Sheet`s that make up this pattern
        """
        if not self._sheets:
            self._extract_sheets()
        return self._sheets

    def save_pdf(self, output_file):
        """
        Save the created pattern as a PDF file.
        """
        writer = PDFWriter(self.sheets())
        writer.create_document(["page", "measure, mark, cut and fold at (cm)"])
        writer.save(output_file)

    def _extract_sheets(self):
        """
        Read the image and set `self._sheets` accordingly.
        """
        image_data = imread(self.input_path, pilmode="RGB")
        for column_index in range(image_data.shape[1]):
            inversions = self._inversion_points(image_data[:, column_index, :])
            self._sheets.append(
                Sheet(
                    [inversion.index for inversion in inversions],
                    self.measurement_interval,
                    page_number=(column_index * 2 + self.start_page)
                    )
                )

    def _inversion_points(self, image_column):
        """
        Return information about color changes as a list of `InversionPoint`s

        The resulting `InversionPoint`s each have the following attributes:
         - `index`: the index of the pixel whose color differs from the one
                    before it
         - `from_color`: color of the previous pixel
         - `to_color`: the color of the latter pixel

        :image_column: A list of pixels colors
        """
        # pylint: disable=no-self-use
        inversion_points = []
        for i in range(1, len(image_column)):
            if (image_column[i-1] != image_column[i]).any():
                inversion_points.append(InversionPoint(i,
                                                       image_column[i-1],
                                                       image_column[i]))
        return inversion_points
