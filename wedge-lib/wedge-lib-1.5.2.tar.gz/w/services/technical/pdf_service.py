from django.template.loader import render_to_string
from weasyprint import HTML, CSS
from weasyprint.fonts import FontConfiguration

from w.services.technical.filesystem_service import FilesystemService


class PdfService:
    @classmethod
    def generate(cls, content) -> bytes:
        """
        Generate PDF binary data.

        Args:
            content (str|dict): message or template (as dict) :
                    {"template_name": <str>, "context": <dict> }

        Returns:
            bytes: pdf binary data
        """
        if not content:
            raise RuntimeError("Can't generate pdf binary with empty content provided")

        # html content
        if isinstance(content, dict):
            content = render_to_string(**content)
        html = HTML(string=content)

        # create pdf content
        font_config = FontConfiguration()
        # Warning : this overrides the font specified in the provided template
        css = CSS(
            string="""
            @font-face {
                font-family: Arial;
            }
            * { font-family: Arial }""",
            font_config=font_config,
        )
        pdf = html.write_pdf(None, stylesheets=[css], font_config=font_config)

        return pdf

    @classmethod
    def write_file(cls, filename, content) -> bytes:
        """
        Create a PDF file.

        Args:
            filename (str): output file path
            content (str|dict): message or template (as dict) :
                {"template_name": <str>, "context": <dict> }

        Returns:
            bytes: pdf binary data
        """

        # Generate PDF binary data
        pdf = cls.generate(content)

        # create file
        FilesystemService.write_binary_file(filename, pdf)

        return pdf
