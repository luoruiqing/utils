# coding:utf-8
from jieba import cut_for_search


def cut_words(string, star=";", iter=False, *arg, **kwargs):
    """ jieba分词 cut_for_search """
    _iter = cut_for_search(string, *arg, **kwargs)
    if iter:
        return _iter
    return star.join(_iter)
