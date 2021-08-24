# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pypki3']

package_data = \
{'': ['*']}

install_requires = \
['cryptography', 'temppath']

setup_kwargs = {
    'name': 'pypki3',
    'version': '2021.236.951',
    'description': 'More user-friendly way to access PKI-enabled services.',
    'long_description': '# pypki3\n\npypki3 is intended as a replacement for pypki2.\nIt is built around the `cryptography` package instead of `pyOpenSSL`, which is now deprecated.\n\nUnlike pypki2, pypki3 does not try to do any auto-configuration, nor does it try to silently compensate when there\'s a configuration issue.  The mantra is, "Let it crash."\n\npypki3 also does not support any monkey-patching like pypki2 did.  There\'s just no need for that.\n\n## Configuration\n\nSince the user has to create their own configuration file now, the config file is much simpler, using a standard `config.ini` format, of the following form.\n\n```\n[global]\np12 = /path/to/your.p12\npem = /path/to/your.combined.pem\nca = /path/to/certificate_authorities.pem\n```\n\nAt least one of `p12` or `pem` must be populated.  If both are populated, then `p12` is used.\n\nThe `pem` file must be a combined key-and-cert file of the following form, which is pretty normal in the Python world.\n\n```\n-----BEGIN RSA PRIVATE KEY-----\n... (private key in base64 encoding) ...\n-----END RSA PRIVATE KEY-----\n-----BEGIN CERTIFICATE-----\n... (certificate in base64 PEM encoding) ...\n-----END CERTIFICATE-----\n```\n\n### Configuration file locations\n\npypki3 will first look at the location specified by the `PYPKI3_CONFIG` environment variable for a config file.  This can be helpful in corporate Windows environments where the "home directory" is not always in a standard location.  It can also be useful in test environments.\n\nNext pypki3 will look in `~/.config/pypki3/config.ini`.\n\nFinally, pypki3 will look in `/etc/pypki3/config.ini`.\n\n## Usage\n\n### Get an SSLContext\nIf you have your own code and you just want to pass along an SSLContext based on the .mypki config (eg. for `urlopen()`, or for the `requests` package), then all you have to do is the following:\n\n```python\nfrom urllib.request import urlopen\nimport pypki3\nctx = pypki3.ssl_context()\nresp = urlopen(https_url, context=ctx)\n...\n```\n\nIf you have already configured your PKI info, you have the option of providing a certificate password to `ssl_context()` rather than using the interactive prompt.  This can be useful when the password is stored in a vault, or when the code needs to run in some non-interactive way.  Please be conscientious of the security implications of putting your password directly in your code though.\n\n```python\nfrom urllib.request import urlopen\nimport pypki3\nctx = pypki3.ssl_context(password=\'supersecret\')\nresp = urlopen(https_url, context=ctx)\n...\n```\n\n### Prompting for a password early (optional)\n\nSometimes it can also be useful to force the certificate password prompt to appear before `ssl_context()` is called, by another library for example.  To do this, simply use `prepare()`.\n\n```python\nimport pypki3\nimport another_library_that_uses_pypki3\npypki3.prepare()  # Prompts for password here\n\n# A lot of other code/steps...\n\n# Does not prompt for password way down here\nanother_library_that_uses_pypki3.does_something()\n```\n\n### Getting a decrypted key/cert context\n\npypki3 includes a context manager that ensures the decrypted key and cert are cleaned up.  This is useful when you want to make sure you don\'t leave your decrypted certs sitting around on disk.\n\n```python\nimport pypki3\n\nwith NamedTemporaryKeyCertPaths() as key_cert_paths:\n    key_path = key_cert_paths[0]  # key_path is a pathlib.Path object\n    cert_path = key_cert_paths[1]  # cert_path is a pathlib.Path object\n    # Do something awesome here\n\n# Decrypted key and cert are cleaned up when you leave the `with` context.\n```\n\n### Using the pip wrapper\nSome pip servers require PKI authentication.  To make this a bit easier, pypki3 includes a pip wrapper that takes care of filling in the `--client-cert` and `--cert` parameters based on the pypki3 configuration.  This also prevents pip from prompting for a password 8 million times when use password-protected (encrypted) certs.\n\n```python\nimport pypki3\npypki3.pip([\'install\', \'amazing-internal-package\'])\n```\n',
    'author': 'Bill Allen',
    'author_email': 'billallen256@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'http://github.com/nbgallery/pypki3',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7',
}


setup(**setup_kwargs)
