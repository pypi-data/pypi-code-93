from string import Template

from IPython.display import display, HTML
try:
    from google.colab.output import eval_js
except:
    def eval_js(js):
        body = HTML(f"""<script>
        {js}
        </script>""")
        display(body)


from .cannon_html import HTML_TEMPLATE, SCRIPT


def cannon_game(powder):
    html_source = Template(HTML_TEMPLATE)
    html_body = HTML(html_source.substitute(**{"SCRIPT":SCRIPT, "stage":1, "powder":powder}))
    display(html_body)


def cannon_game2(powder):
    html_source = Template(HTML_TEMPLATE)
    html_body = HTML(html_source.substitute(**{"SCRIPT":SCRIPT, "stage":2, "powder":powder}))
    display(html_body)
