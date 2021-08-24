import setuptools
with open("./ConversationAgent/README.md", "r") as fh:
  long_description = fh.read()
setuptools.setup(
    name='ConversationAgent',
    version='0.3.4',
    description='ConversationAgent',
    author='Theta',
    license='',
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    package_data={
        "": ["*.txt", "*.py", "*.md"]
    },
    zip_safe=False
)

