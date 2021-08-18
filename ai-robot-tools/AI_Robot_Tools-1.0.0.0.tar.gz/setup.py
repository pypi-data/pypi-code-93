from setuptools import setup, find_packages
import codecs
import os

VERSION = '1.0.0.0'
DESCRIPTION = 'AI_Robot_Tools'
LONG_DESCRIPTION = 'A package to AI Robot Tools'

# Setting up
setup(
    name="AI_Robot_Tools",
    version=VERSION,
    author="Rishabh",
    author_email="rinku87096@gmail.com",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    install_requires=['pyttsx3','SpeechRecognition','Pyaudio','googletrans'],
    keywords=['Speak', 'Speech', 'Speak and Speech Tools','AI Robot Tools', 'AI Jarvis', 'python tutorial', 'Rishabh'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)