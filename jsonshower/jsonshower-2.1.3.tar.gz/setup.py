from setuptools import setup, find_packages

EXTRAS_REQUIRE = {
    "pdfs": ["pdf-annotate", "pdf2image"]
}

setup(
    name='jsonshower',
    version='2.1.3',
    url='https://github.com/RelevanceAI/jsonviewer',
    author='Jacky Wong',
    author_email='jacky.wong@vctr.ai',
    description='Json Viewer with additional multimedia and highlighting support',
    packages=find_packages(),
    install_requires=['pandas'],
    extras_require=EXTRAS_REQUIRE
)
