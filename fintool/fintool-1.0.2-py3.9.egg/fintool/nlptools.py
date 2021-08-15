import sys
import pickle
import stem
import stem.connection
import time
import urllib
from tqdm import tqdm
from stem import Signal
from stem.control import Controller
from random_user_agent.user_agent import UserAgent
from random_user_agent.params import SoftwareName, OperatingSystem
import numpy as np
import pandas as pd
from requests_html import HTMLSession
from requests_html import AsyncHTMLSession
from lxml import html
import requests
from lxml import etree
import re
from re import sub
from decimal import Decimal
import datetime
from html.parser import HTMLParser
from bs4 import BeautifulSoup
import os
import csv
import json
import subprocess
import threading
import logging
import multiprocessing
import sqlite3
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from nltk.corpus import state_union
from nltk.tokenize import PunktSentenceTokenizer
from bs4 import BeautifulSoup
from multiprocessing import Process, Manager, Value
from . import utils as scu

def readfile(filepath):
    with open(filepath) as f:
        return f.read()

def cleanse_html(txt):
    soup = BeautifulSoup(txt, 'html.parser')
    ptags = soup.find_all('p')
    sent = ""
    for ptag in ptags:
        sent += str(ptag)
        tags = re.compile(r'''(<a.*?>)''').findall(sent)
        tags += re.compile(r'''(<sup.*?sup>)''').findall(sent)
        patterns = [r'''(<a.*?">)''', r'''(<sup.*?sup>)''', r'''(<\/a>)''', r'''(</p>)''', r'''(<p>)''',
        r'''(<b>)''', r'''(</b>)''', r'''(<i>)''', r'''(</i>)''', r'''<p.*?>''']
        matches = []
        for pt in patterns:
            for match in re.compile(pt).finditer(sent):
                matches += [match]
                start, end = match.span()
                # sent = sent[:start] + sent[end:]
                sent = sent[:start] + "@"*(end-start) + sent[end:]
        sent = sent.replace("\n", "@ ")
        sent = sent.replace("@", "")
    return sent
