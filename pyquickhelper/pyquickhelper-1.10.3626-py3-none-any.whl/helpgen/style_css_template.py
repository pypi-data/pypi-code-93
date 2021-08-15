"""
@file
@brief Custom style for the documentation.
"""

#: style for thumbnails
style_figure_notebook = "style_notebook_snippet.css", """
div.sphx-pyq-thumb {
    box-shadow: none;
    background: #FFF;
    margin: 5px;
    padding-top: 5px;
    min-height: 230px;
    border: solid white 1px;
    -webkit-border-radius: 5px;
    -moz-border-radius: 5px;
    border-radius: 5px;
    float: left;
    position: relative;
}

div.sphx-pyq-thumb:hover {
    box-shadow: 0 0 15px rgba(142, 176, 202, 0.5);
    border: solid #B4DDFC 1px; }
    div.sphx-pyq-thumb a.internal {
    display: block;
    position: absolute;
    padding: 150px 10px 0px 10px;
    top: 0px;
    right: 0px;
    bottom: 0px;
    left: 0px;
}

div.sphx-pyq-thumb p {
    margin: 0 0 .1em 0;
}

div.sphx-pyq-thumb .figure {
    margin: 10px;
    width: 160px;
}

div.sphx-pyq-thumb img {
    max-width: 100%;
    max-height: 160px;
    display: inline;
}

div.sphx-pyq-thumb[tooltip]:hover:after {
    background: rgba(0, 0, 0, 0.8);
    -webkit-border-radius: 5px;
    -moz-border-radius: 5px;
    border-radius: 5px;
    color: white;
    content: attr(tooltip);
    left: 95%;
    padding: 5px 15px;
    position: absolute;
    z-index: 98;
    width: 220px;
    bottom: 52%;
}

div.sphx-pyq-thumb[tooltip]:hover:before {
    content: "";
    position: absolute;
    z-index: 99;
    border: solid;
    border-color: #333 transparent;
    border-width: 18px 0px 0px 20px;
    left: 85%;
    bottom: 58%;
}

.sphx-pyq-download {
    background-color: #ffc;
    border: 1px solid #c2c22d;
    border-radius: 4px;
    margin: 1em auto 1ex auto;
    max-width: 45ex;
    padding: 1ex;
}

.sphx-pyq-download a {
    color: #4b4600;
}
"""


#: base string for creating the thumbnail, layout=classic
THUMBNAIL_TEMPLATE = """
.. raw:: html

    <div class="sphx-pyq-thumb" tooltip="{snippet}">

.. only:: html

    .. figure:: /{thumbnail}

        :ref:`{ref_name}`

.. raw:: html

    </div>
"""

#: base string for creating the thumbnail, layout=table
THUMBNAIL_TEMPLATE_TABLE = """    * - .. image:: /{thumbnail}
            :target: {nb_name}
      - :ref:`{ref_name}`
      - {snippet}"""
