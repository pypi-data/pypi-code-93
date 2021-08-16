"""Print number of PAGes in PDF files.

This simple utility prints file counter, number of pages and filename
for each given pdf file. Fields are separated by a '\\t' (horizontal tab)
character.

Non-pdf files are silently skipped.

Empty or erroneous pdf files are reported as containing zero pages.

Examples:

    $ pagpdf * # list number of pages of all pdf files in current path

    $ pagpdf * 2>/dev/null # leave out warnings from pdfrw.PdfReader

"""

__version__ = "0.9.2"

requires = ["pdfrw >=0.4"]



