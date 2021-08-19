from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(name='pika-wrapper',
      version='0.0.5',
      author='MrShved',
      author_email='2100992@gmail.com',
      description='Simple wrapper around Pika to make it easier to work with.',
      package_dir={"": "src"},
      packages=find_packages(where="src"),
      install_required=[
          'pika==1.2.0'
      ],
      url='https://github.com/2100992/pika_wrapper',
      zip_safe=False,
      keywords=["pika", "rabbitmq", "amqpy"],
      package_data={"pika-wrapper": ["requirements.txt"]},
      include_package_data=True,

      classifiers=[
          "Programming Language :: Python",
          "License :: OSI Approved :: MIT License",
          "Development Status :: 3 - Alpha",
          "Intended Audience :: Developers"
      ],
      long_description_content_type="text/markdown",
      long_description=long_description,
      python_requires=">=3.6"
      )
