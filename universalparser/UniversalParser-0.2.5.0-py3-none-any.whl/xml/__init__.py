from xml.parsers.expat import ParserCreate, ExpatError, errors

xml_data = """
<root>
    <a name="name_a">I am A.</a>
    <b name="name_b">
        <c name="name_c"  flag="1">I am C.</c>
        <c name="name_$c" flag="1">I am CC.</c>
        <c>666</c>
        <c>hello</c>
        <c>
            <d name="d">world</d>
            123
            <e name="e"></e>
            <hh></hh>
        </c>
    </b>
</root>
"""

