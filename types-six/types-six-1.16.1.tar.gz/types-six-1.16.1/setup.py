from setuptools import setup

name = "types-six"
description = "Typing stubs for six"
long_description = '''
## Typing stubs for six

This is a PEP 561 type stub package for the `six` package.
It can be used by type-checking tools like mypy, PyCharm, pytype etc. to check code
that uses `six`. The source for this package can be found at
https://github.com/python/typeshed/tree/master/stubs/six. All fixes for
types and metadata should be contributed there.

See https://github.com/python/typeshed/blob/master/README.md for more details.
This package was generated from typeshed commit `e4879abb59e53d90a301f522574813b0010519e6`.
'''.lstrip()

setup(name=name,
      version="1.16.1",
      description=description,
      long_description=long_description,
      long_description_content_type="text/markdown",
      url="https://github.com/python/typeshed",
      install_requires=[],
      packages=['six-stubs', 'six-python2-stubs'],
      package_data={'six-stubs': ['__init__.pyi', 'moves/reprlib.pyi', 'moves/builtins.pyi', 'moves/_thread.pyi', 'moves/socketserver.pyi', 'moves/tkinter_dialog.pyi', 'moves/email_mime_nonmultipart.pyi', 'moves/_dummy_thread.pyi', 'moves/email_mime_text.pyi', 'moves/SimpleHTTPServer.pyi', 'moves/__init__.pyi', 'moves/http_cookiejar.pyi', 'moves/tkinter_commondialog.pyi', 'moves/cPickle.pyi', 'moves/tkinter_filedialog.pyi', 'moves/urllib_robotparser.pyi', 'moves/configparser.pyi', 'moves/urllib_error.pyi', 'moves/urllib_request.pyi', 'moves/collections_abc.pyi', 'moves/email_mime_multipart.pyi', 'moves/tkinter_ttk.pyi', 'moves/queue.pyi', 'moves/http_cookies.pyi', 'moves/tkinter_constants.pyi', 'moves/urllib_response.pyi', 'moves/http_client.pyi', 'moves/urllib_parse.pyi', 'moves/html_entities.pyi', 'moves/tkinter.pyi', 'moves/tkinter_tkfiledialog.pyi', 'moves/email_mime_base.pyi', 'moves/html_parser.pyi', 'moves/BaseHTTPServer.pyi', 'moves/CGIHTTPServer.pyi', 'moves/urllib/parse.pyi', 'moves/urllib/response.pyi', 'moves/urllib/__init__.pyi', 'moves/urllib/robotparser.pyi', 'moves/urllib/error.pyi', 'moves/urllib/request.pyi', 'METADATA.toml'], 'six-python2-stubs': ['__init__.pyi', 'moves/reprlib.pyi', 'moves/xmlrpc_client.pyi', 'moves/_thread.pyi', 'moves/socketserver.pyi', 'moves/email_mime_nonmultipart.pyi', 'moves/_dummy_thread.pyi', 'moves/email_mime_text.pyi', 'moves/SimpleHTTPServer.pyi', 'moves/__init__.pyi', 'moves/http_cookiejar.pyi', 'moves/cPickle.pyi', 'moves/urllib_robotparser.pyi', 'moves/configparser.pyi', 'moves/urllib_error.pyi', 'moves/urllib_request.pyi', 'moves/collections_abc.pyi', 'moves/email_mime_multipart.pyi', 'moves/queue.pyi', 'moves/http_cookies.pyi', 'moves/urllib_response.pyi', 'moves/http_client.pyi', 'moves/urllib_parse.pyi', 'moves/html_entities.pyi', 'moves/email_mime_base.pyi', 'moves/html_parser.pyi', 'moves/BaseHTTPServer.pyi', 'moves/CGIHTTPServer.pyi', 'moves/urllib/parse.pyi', 'moves/urllib/response.pyi', 'moves/urllib/__init__.pyi', 'moves/urllib/robotparser.pyi', 'moves/urllib/error.pyi', 'moves/urllib/request.pyi', 'METADATA.toml']},
      license="Apache-2.0 license",
      classifiers=[
          "License :: OSI Approved :: Apache Software License",
          "Typing :: Typed",
      ]
)
