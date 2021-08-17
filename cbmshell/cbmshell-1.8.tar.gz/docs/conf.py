import sphinx_rtd_theme

# The master toctree document.
master_doc = 'index'

# General information about the project.
project = 'cbmshell'
copyright = '2021, Simon Rowe'
author = 'Simon Rowe'

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = 'sphinx'

# Custom theme from ReadTheDocs
html_theme = 'sphinx_rtd_theme'
html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]
