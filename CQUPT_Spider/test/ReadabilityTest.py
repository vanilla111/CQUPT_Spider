# -*- coding: utf-8 -*-
import requests
from goose3 import Goose
from goose3.text import StopWordsChinese
import re

def read():
    resp = requests.get('http://xwzx.cqupt.edu.cn/cqupt_xwzx/news.jsp?id=F5UU535967G00Y24')
    g = Goose({'stopwords_class': StopWordsChinese})
    content = g.extract(raw_html=resp.text)
    print(content.publish_date)
    print(content.title)
    print(content.cleaned_text)
    print(len(content.cleaned_text))


if __name__ == '__main__':
    # g = re.match('^.*(english|korea).cqupt.edu.cn', 'http://korea.cqupt.edu.cn/adas.jpg')
    # print(g)
    read()