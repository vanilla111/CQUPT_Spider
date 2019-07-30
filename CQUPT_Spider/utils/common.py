# -*- coding: utf-8 -*-
__author__ = "wang"
import hashlib

from elasticsearch_dsl import connections
from CQUPT_Spider.models.CquptEsType import CquptType

es = connections.create_connection()


def get_md5(string):
    if isinstance(string, str):
        string = string.encode("utf-8")
    m = hashlib.md5()
    m.update(string)
    return m.hexdigest()


def gen_suggests(index, info):
    used_words = set()
    suggests = []
    for text, weight in info:
        if text:
            words = es.indices.analyze(index=index, body=text, params={
                'filter': ['lowercase'],
                'analyzer': 'ik_max_word'
            })
            analyzed_words = set([r['token'] for r in words['tokens'] if len(r['token']) > 1])
            new_words = analyzed_words - used_words
            used_words = used_words.union(new_words)
        else:
            new_words = set()
        if new_words:
            suggests.append({'input': list(new_words), 'weight': weight})
    return suggests


def get_main_content(content_list, _limitCount=180, _depth=5, _appendMode=False):
    """
    能够从过滤html标签后的文本中找到正文文本的起止行号，行号之间的文本就是网页正文部分。
    特性：正文部分的文本密度要高出非正文部分很多。
    :param content_list: 去除html标签后的文本，按行拆分为list
    :param _limitCount: 候选文本长度达到该值时，认为进入正文部分
    :param _depth: 每次分析几行数据
    :return: 正文内容
    """
    preTextLen = 0 # 上一次统计的字符数量
    startPos = -1 # 记录文章起始位置
    _headEmptyLines = 2
    _endLimitCharCount = 20
    content = []
    line = []
    for i in range(len(content_list) - _depth):
        length = 0
        for j in range(_depth):
            length += len(content_list[i + j])

        if startPos == -1:
            # 还没找到正文位置
            if (preTextLen > _limitCount) and (length > 0):
                # 查找文章起始位置，发现两行连续为空认为是头部
                emptyCount = 0
                for j in range(i - 1, 0, -1):
                    if isNullOrWhiteSpace(content_list[j]):
                        emptyCount += 1
                    else:
                        emptyCount = 0
                    if emptyCount == _headEmptyLines:
                        startPos = j + _headEmptyLines
                        break
                # 如果没有定位到正文开始，以当前位置为起始
                if startPos == -1:
                    startPos = i
                for j in range(startPos, i + 1):
                    # 将发现的正文放入list
                    content.append(content_list[j])
                    line.append(j)
        else:
            # 如当前长度、上一次长度都小于阈值，认为已经结束，若开启追加模式，则继续往后找
            if length <= _endLimitCharCount and preTextLen < _endLimitCharCount:
                if not _appendMode:
                    break
                startPos = -1
            line.append(i)
            content.append(content_list[i])
        preTextLen = length
    # 返回发现的正文内容
    return '\n'.join(content), [min(line), max(line)] if len(line) > 0 else [0, 0]


def isNullOrWhiteSpace(content):
    return content or len(content) == 0
