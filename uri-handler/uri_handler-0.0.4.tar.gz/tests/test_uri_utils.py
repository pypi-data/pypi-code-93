import pytest
import uri_handler.utils.uri_utils


@pytest.mark.parametrize(
    "uri,stargs_to_join,expected_joined_uri",
    [
        # test uri
        ("s3://mybucket/path/to",
         ("thing",),
         "s3://mybucket/path/to/thing"),
        # test src uri ending in /
        ("s3://mybucket/path/to/",
         ("thing",),
         "s3://mybucket/path/to/thing"),
        # test multiple uri join arguments
        ("s3://mybucket/path/to",
         ("some/even/", "deeper", "thing",),
         "s3://mybucket/path/to/some/even/deeper/thing"),
        # test standard file uri
        ("file:///path/to/",
         ("thing",),
         "file:///path/to/thing"),
        # test nonstandard (single / scheme) file uri
        ("file:/path/to",
         ("thing",),
         "file:///path/to/thing"),
        # uri with all components (except obsolete ;parameters)
        ("myscheme://mynetloc/path/to?myqparam=null&myotherqparam=null#myfragment",
         ("thing",),
         "myscheme://mynetloc/path/to/thing?myqparam=null&myotherqparam=null#myfragment")
    ])
def test_join_uri(uri, stargs_to_join, expected_joined_uri):
    """test join uri for various uris"""
    r = uri_handler.utils.uri_utils.uri_join(uri, *stargs_to_join)

    assert r == expected_joined_uri


@pytest.mark.parametrize(
    "uri,expected_prefix", [
        # full uri with
        ("myscheme://mynetloc/path/to/thing?myqparam=null&myotherqparam=null#myfragment",
         "myscheme://mynetloc/path/to?myqparam=null&myotherqparam=null#myfragment"),
        # uri with trailing / in path
        ("myscheme://mynetloc/path/to/path/?myqparam=null&myotherqparam=null#myfragment",
         "myscheme://mynetloc/path/to?myqparam=null&myotherqparam=null#myfragment"),
        # uri at top level
        ("myscheme://mynetloc/mything?myqparam=null&myotherqparam=null#myfragment",
         "myscheme://mynetloc/?myqparam=null&myotherqparam=null#myfragment"),
        # uri of top level (acts like os.path.dirname)
        ("myscheme://mynetloc/?myqparam=null&myotherqparam=null#myfragment",
         "myscheme://mynetloc/?myqparam=null&myotherqparam=null#myfragment"),
    ])
def test_uri_prefix(uri, expected_prefix):
    r = uri_handler.utils.uri_utils.uri_prefix(uri)

    assert r == expected_prefix
