#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" Detector de violencia de género en redes sociales. """

import csv
import io
import json
import numpy as np
import os
import pandas as pd
import re
import Stemmer
import sys
import time
from collections import Counter


__author__ = "Miguel Salazar, Jorge Martínez, Fernando Aguilar"
__license__ = "GPL"
__version__ = "1.0"
__status__ = "Prototype"


token_list = ['URL', 'EMAIL', 'MENTION', 'HASHTAG', 'NUMBER', 'EMOTICON', 'EMOJI']


def load_dataset(dataset):
    print("loading dataset...")

    path = os.path.dirname(os.path.abspath(__file__))
    filename = os.path.join(path,"data",dataset)
    tweets = []

    with open(filename) as fin:
        reader = csv.reader(fin)
        for row in reader:
            tweet = row[0].split("_sep_")
            tweets.append(tweet[1])
    return tweets


def load_dictionary():
    filename = "data/dict.txt"
    dictionary = []
    with open(filename) as fin:
        reader = csv.reader(fin)
        for word in reader:
            dictionary.append(word[0])
    return dictionary


def tokenize(txt, emoticons=None, emojis=None):
    if emoticons is None:
        raise ValueError('You must provide an emoticons list')
    if emojis is None:
        raise ValueError('You must provide an emojis list')

    x = txt
    x = re.sub("(https?|ftp|file)://[-a-zA-Z0-9+&@#/%?=~_|!:,.;]*[-a-zA-Z0-9+&@#/%=~_|]", " URL ", x)
    x = re.sub("^[_A-Za-z0-9-\\\\+]+(\\\\.[_A-Za-z0-9-]+)*@[A-Za-z0-9-]+(\\\\.[A-Za-z0-9]+)*(\\\\.[A-Za-z]{2,})$", " EMAIL ", x)
    x = re.sub("@[A-Za-z0-9]+", " MENTION ", x)
    x = re.sub("#[A-Za-z0-9]+", " HASHTAG ", x)
    x = re.sub("\\d+(\\.\\d*)?°?", " NUMBER ", x)
    for em in emoticons:
        x = x.replace(em, ' EMOTICON ')
    for ej in emojis:
        x = x.replace(ej, ' EMOJI ')
    x = re.sub(u'['u'\U0001F300-\U0001F64F'u'\U0001F680-\U0001F6FF'u'\u2600-\u26FF\u2700-\u27BF]+', ' EMOJI ', x)
    return x


def remove_punctiation(txt):
    x = re.sub("[\\\"\\$%&@\\.,:;\\(\\)¿\\?`+\\-_\\*=!¡\\\\/#{}\\[\\]]", " ", txt)
    return x


def strim_space(txt):
    """
    Strip and trim whitespace characters
    :param txt:
    :return:
    """
    x = txt.strip()
    x = re.sub("\\s+", " ", txt)
    return x


def lowercase(words_list):
    li = [w.lower() if not w in token_list else w for w in words_list]
    return li


def remove_stopwords(words_list, stopwords_list):
    words_nonstop = [w for w in words_list if not w in stopwords_list]
    return words_nonstop


def stem(words_list):
    # TODO: How to detect language!?
    stemmer = Stemmer.Stemmer('spanish')
    words_stemmed = stemmer.stemWords(words_list)
    return words_stemmed


def preprocess(txt, emoticons=None, emojis=None):
    x = tokenize(txt, emoticons=emoticons, emojis=emojis)
    x = remove_punctiation(x)
    x = strim_space(x)
    return x


# Gets a dictionary with the frequency count of each word in the corpus.
def tf_vector(txt, stopwords=None, emoticons=None, emojis=None):
    """
    Transform a string into a Term-Frecuency dictionary
    :param txt: Text to process
    :param stopwords: A list of string of stopwords
    :param emoticons: A list of string of emoticons (see __main__ in this script)
    :param emojis: A list of string of emoticons (see __main__ in this script)
    :return: a dict object in the form {term=count}, with all terms preprocessed
    """
    if stopwords is None:
        raise ValueError('You must provide a stopwords list')
    if emoticons is None:
        raise ValueError('You must provide an emoticons list')
    if emojis is None:
        raise ValueError('You must provide an emojis list')
    if not isinstance(txt, str):
        raise ValueError('txt must be a string')

    x = preprocess(txt, emoticons=emoticons, emojis=emojis)

    words = x.split(' ')
    words = lowercase(words)
    words = remove_stopwords(words, stopwords)
    words = stem(words)

    return dict(Counter(words))


# Vector space model
def get_similarity(tw_vector, dict_vector):
    keys_tweet = set(tw_vector.keys())
    keys_dict = set(dict_vector.keys())
    intersection = keys_tweet & keys_dict

    num = 0
    for element in intersection:
        num += tw_vector[element] * dict_vector[element]

    denA = 0
    for element in tw_vector:
        denA += tw_vector[element]**2

    denB = 0
    for element in dict_vector:
        denB += dict_vector[element]**2

    similarity = num/(denA*denB)

    return similarity


def main():
    print("DeViGeR")
    dictionary = load_dictionary()
    tweets = load_dataset("train.txt")

    stops = open('data/stopwords_spanish.txt').read().splitlines()
    emos = open('data/emoticons.txt').read().splitlines()
    emoj = list(pd.read_csv('data/emojis.csv')['emoji'])

    bow = {}
    dict_vector = tf_vector((" ").join(dictionary), stopwords=stops, emoticons=emos, emojis=emoj)
    for tweet in tweets:
        tw_vector = tf_vector(tweet, stopwords=stops, emoticons=emos, emojis=emoj)
        similarity = get_similarity(tw_vector, dict_vector)


if __name__ == '__main__':
    main()
