import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="socialscore",
    version="2.1",
    author="Ravin Kumar",
    author_email="mr.ravin_kumar@hotmail.com",
    description="Calculate the score of a social media profile and posts on twitter and other social media sites on the internet",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/mr-ravin/social_score",
    keywords = ['Social Score', 'Social Media', 'Network','Social Network'],   # Keywords that define your package best
    install_requires=[            # I get to this in a second
          'tweepy',
      ],

    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
