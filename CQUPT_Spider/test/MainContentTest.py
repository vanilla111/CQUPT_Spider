# -*- coding: utf-8 -*-
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from goose3 import Goose
from goose3.text import StopWordsChinese
from goose3.cleaners import DocumentCleaner
from goose3 import Crawler
from goose3.configuration import Configuration
from w3lib.html import remove_tags
import requests
from CQUPT_Spider.utils.common import get_main_content

#url = "http://xwzx.cqupt.edu.cn/cqupt_xwzx/news.jsp?id=5U5933J7L60QL982"
#url = "http://yjs.cqupt.edu.cn/info/1006/4248.htm"
url = "http://cxy.cqupt.edu.cn/info/1105/1282.htm"
#url = "http://xylyh.cqupt.edu.cn/info/1009/1786.htm"
g = Goose({'stopwords_class': StopWordsChinese})

resp = requests.get(url)
content = g.extract(raw_html=resp.text.encode(resp.encoding).decode(resp.apparent_encoding))
# print(content.cleaned_text)

# 清理标签
config = Configuration()
doc_clean = DocumentCleaner(config , None)
crawler = Crawler(config)
elemetn_html = doc_clean.clean(crawler.get_document(resp.text.encode(resp.encoding).decode(resp.apparent_encoding)))
no_tags_html = elemetn_html.text_content()

# 绘图参数
html_content_list = no_tags_html.splitlines()
line_length = [len(line.strip()) for line in html_content_list]
lines = [line.strip() for line in no_tags_html.splitlines()]
main_content, content_lines = get_main_content(lines)
print(main_content)
print(content_lines)
main_line_x = [i for i in range(content_lines[0], content_lines[1] + 1)]
print(main_line_x)
main_line_y = line_length[main_line_x[0]: main_line_x[-1] + 1]
print(main_line_y)
plt.text(main_line_x[0], main_line_y[0], main_line_x[0])
plt.text(main_line_x[-1], main_line_y[-1], main_line_x[-1])
#plt.xlim((100, 300))
plt.rcParams['font.sans-serif'] = ["Microsoft YaHei"]
plt.plot(line_length)
plt.grid(True, linestyle='-.')
plt.title(content.title)
plt.xlabel('行号')
plt.ylabel('该行字符长度')
#plt.savefig('3.png')
plt.show()


# plt.plot(main_line_x, main_line_y)
# plt.show()
# print(main_content)