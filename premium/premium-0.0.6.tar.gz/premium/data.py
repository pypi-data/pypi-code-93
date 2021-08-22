#!/usr/bin/env python

import os

import codefast as cf
import numpy as np

class stopwords:
    english = cf.io.read(
        os.path.join(cf.io.dirname() + '/localdata/en_stopwords.txt'))


class Math:
    @classmethod
    def get_coefs(cls, word, *arr):
        return word, np.asarray(arr, dtype='float32')


class Urls:
    prefix = 'http://filedn.com/lCdtpv3siVybVynPcgXgnPm/corpus'


def fetch_data(fpath: str) -> None:
    cf.info(f'Downloading {fpath}')
    online_url = os.path.join(Urls.prefix, fpath)
    dest = f'/tmp/{cf.io.basename(fpath)}'
    if cf.io.exists(dest):
        msg = f'File {dest} already existed, press [y] to overwrite: '
        if input(msg) == 'y':
            cf.net.download(online_url, dest)
    else:
        cf.net.download(online_url, dest)

    # unzip data if necessary
    if fpath.endswith(('.zip', '.gz')):
        cf.info(f'Unzip file {fpath}')
        cf.shell(f'7z x {dest} -o/tmp -y')
        cf.info(f'7z {dest} completes, removing compressed file...')
        cf.shell(f'rm {dest}')


class WordToVector:
    def __init__(self) -> None:
        self.vectors = {
            'glove-twitter-25': ('glove.twitter.27B.25d.txt',
                                 'pretrained/glove.twitter.27B.25d.txt.gz'),
            'glove-twitter-50': ('glove.twitter.27B.50d.txt',
                                 'pretrained/glove.twitter.27B.50d.txt.gz'),
            'glove-twitter-100': ('glove.twitter.27B.100d.txt',
                                  'pretrained/glove.twitter.27B.100d.txt.gz'),
            'glove-twitter-200': ('glove.twitter.27B.200d.txt',
                                  'pretrained/glove.twitter.27B.200d.txt.gz'),
            'glove-wiki-gigaword-50':
            ('glove.6B.50d.txt', 'pretrained/glove.6B.50d.txt'),
            'glove-wiki-gigaword-100':
            ('glove.6B.100d.txt', 'pretrained/glove.6B.100d.txt'),
            'glove-wiki-gigaword-200':
            ('glove.6B.200d.txt', 'pretrained/glove.6B.200d.txt'),
            'glove-wiki-gigaword-300':
            ('glove.6B.300d.txt', 'pretrained/glove.6B.300d.txt'),
            'google-news-negative-300':
            ('GoogleNews-vectors-negative300.bin', 'pretrained/GoogleNews-vectors-negative300.bin'),
        }

    @property
    def list(self) -> list:
        return list(self.vectors)

    def load_local(self, vector_file:str)->dict:
        return dict(
            Math.get_coefs(*o.strip().split()) for o in cf.io.iter(vector_file))


    def load(self, vector: str = 'glove-twitter-25'):
        if vector not in self.vectors:
            cf.warning(f'{vector} was not here')
            fetch_data(self.vectors[vector][1])

        file_name, url = self.vectors[vector]
        file_name = f'/tmp/{file_name}'
        if not cf.io.exists(file_name):
            fetch_data(url)

        cf.info(f'loading {vector}')
        if vector != 'google-news-negative-300':
            return dict(
                Math.get_coefs(*o.strip().split()) for o in cf.io.iter(file_name))
        else:
            return KeyedVectors.load_word2vec_format('/tmp/GoogleNews-vectors-negative300.bin', binary=True)


word2vec = WordToVector()


class Downloader:
    def douban_movie_review(self):
        '''Kaggle dataset https://www.kaggle.com/liujt14/dou-ban-movie-short-comments-10377movies
        size: 686 MB
        '''
        cf.info(
            'Downloading douban movie review data: https://www.kaggle.com/liujt14/dou-ban-movie-short-comments-10377movies',
        )
        fetch_data('douban_movie_review.zip')

    def douban_movie_review_2(self):
        fetch_data('douban_movie_review2.csv.zip')

    def chinese_mnist(self):
        '''https://www.kaggle.com/fedesoriano/chinese-mnist-digit-recognizer'''
        fetch_data('Chinese_MNIST.csv.zip')

    def toxic_comments(self):
        fetch_data('toxic_comments.csv')

    def icwb(self):
        '''Data source: http://sighan.cs.uchicago.edu/bakeoff2005/
        '''
        fetch_data('icwb2-data.zip')

    def news2016(self):
        ''' 中文新闻 3.6 GB 2016年语料 
        '''
        fetch_data('news2016.zip')

    def msr_training(self):
        fetch_data('msr_training.utf8')

    def realty_roles(self):
        fetch_data('realty_roles.zip')
        cf.info('unzip files to /tmp/customer.txt and /tmp/salesman.txt')

    def realty(self):
        import getpass
        cf.info("Download real estate dataset realty.csv")
        zipped_data = os.path.join(Urls.prefix, 'realty.zip')
        cf.net.download(zipped_data, '/tmp/realty.zip')
        passphrase = getpass.getpass('Type in your password: ').rstrip()
        cf.utils.shell(f'unzip -o -P {passphrase} /tmp/realty.zip -d /tmp/')

    def spam_en(self):
        cf.info(f'Downloading English spam ham dataset to')
        fetch_data('spam-ham.txt')

    def spam_cn(self, path: str = '/tmp/'):
        cf.info(f'Downloading Chinese spam ham dataset to {path}')
        zipped_data = os.path.join(Urls.prefix, 'spam_cn.zip')
        label_file = os.path.join(Urls.prefix, 'spam_cn.json')
        cf.net.download(zipped_data, '/tmp/tmp_spam.zip')
        cf.utils.shell('unzip -o /tmp/tmp_spam.zip -d /tmp/')
        cf.net.download(label_file, '/tmp/spam_cn.json')


downloader = Downloader()
