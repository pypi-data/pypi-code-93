from setuptools import setup

setup(
    name='opportini_pdfbuilder',
    version='0.1.0',
    author='Menno',
    author_email='phoenix.ts1991@gmail.com',
    url='https://github.com/competition-index/opportini_html2pdf/',
    packages=['html2pdf_converter', 'html2pdf_converter.tools'],
    description='HTML to PDF with Python-Jinja',
    long_description=open('README.md').read(),
    keywords=[],
    install_requires=[
        'selenium==3.141.0',
        'jinja2==2.11.3'
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.5',
    ]
)
