from sklearn.base import BaseEstimator
from sklearn.pipeline import Pipeline
import logging
from sklearn.preprocessing import Normalizer
from argmining.models.stts import STTS_TAGSET
from argmining.models.uts import UTS_TAGSET, get_UTS_tag
from collections import OrderedDict
import numpy as np
from sklearn.feature_selection import SelectKBest, chi2


def build():
    pipeline = Pipeline([('transformer',
                          StructuralFeatures(use_STTS=False)),
                         ])
    return ('structural_features', pipeline)


class StructuralFeatures(BaseEstimator):
    def __init__(self, use_sentence_length=True):
        self.logger = logging.getLogger()

    def fit(self, X, y):
        return self

    def transform(self, X):
        transformed = list(map(lambda x: self.transform_sentence(x), X))
        return transformed

    def transform_sentence(self, thf_sentence):
        values = []
        words = list(map(lambda token: token.text, thf_sentence.tokens))
        comma_relative = words.count(',') / float(len(words))
        dot_relative = words.count('.') / float(len(words))
        values.append(comma_relative)
        values.append(dot_relative)
        values.append(len(words))
        link_count = 0
        for word in words:
            if word.startswith('www.') or word.startswith('http'):
                link_count += 1
        values.append(float(link_count))
        last_word = words[len(words) - 1]

        if last_word == '.':
            values.append([1.0, 0.0, 0.0, 0.0])
        elif last_word == '!':
            values.append([0.0, 1.0, 0.0, 0.0])
        elif last_word == '?':
            values.append([0.0, 0.0, 1.0, 0.0])
        else:
            values.append([0.0, 0.0, 0.0, 1.0])
        return values
