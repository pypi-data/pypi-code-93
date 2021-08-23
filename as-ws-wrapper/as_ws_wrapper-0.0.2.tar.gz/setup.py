from setuptools import setup

# versioning
import versioneer

with open("README.md", "r") as fh:
    long_description = fh.read()


setup(
    name="as_ws_wrapper",
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    author="Imobanco",
    description="Cliente não oficial do webservice Accesstage",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/imobanco/as-ws-wrapper/",
    packages=[
        "as_ws_wrapper",
        "as_ws_wrapper.wrapper",
        "as_ws_wrapper.models",
        "as_ws_wrapper.adapters",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Environment :: Web Environment",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Natural Language :: Portuguese (Brazilian)",
        "Operating System :: OS Independent",
        "Topic :: Documentation :: Sphinx",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content :: CGI Tools/Libraries",
        "Topic :: Utilities",
        "",
        "",
    ],
    python_requires=">=3.8",
    install_requires=["python-decouple>=3.3", "pydantic>=1.7.0", "zeep>=4.0.*"],
    project_urls={
        # "Documentation": "https://bb-wrapper.readthedocs.io",
        "Source": "https://github.com/imobanco/as-ws-wrapper",
        "Tracker": "https://github.com/imobanco/as-ws-wrapper/issues",
    },
)
