# -*- coding: utf-8 -*-
import time
import numpy as np
from matplotlib import pyplot as plt
import MySQLdb
import requests
from goose3.cleaners import DocumentCleaner
from goose3 import Crawler
from goose3.configuration import Configuration
from CQUPT_Spider.utils.common import get_main_content


db = MySQLdb.connect('localhost', 'root', '', 'cqupt', charset='UTF8')
cursor = db.cursor()
cursor.execute("SELECT * FROM main_content_sample")
res = cursor.fetchall()

if len(res) < 100:
    cursor.execute(
        "SELECT url,html_title,content FROM cqupt_search_back WHERE content != 'None' AND content != '' ORDER BY RAND() LIMIT 100")
    res = cursor.fetchall()
    i = 1
    for r in res:
        resp = requests.get(r[0])
        # 清理标签
        config = Configuration()
        doc_clean = DocumentCleaner(config, None)
        crawler = Crawler(config)
        elemetn_html = doc_clean.clean(crawler.get_document(resp.text.encode(resp.encoding).decode(resp.apparent_encoding)))
        no_tags_html = elemetn_html.text_content()
        _sql = "INSERT INTO main_content_sample(url,title,html,content) VALUES (%s,%s,%s,%s)"
        #print(_sql)
        print("正在插入第{0}条数据".format(i))
        i += 1
        cursor.execute(_sql, (r[0], r[1], no_tags_html, r[2]))
        db.commit()

# 设定计算规则，若提取出的正文字符数为n,真正的字符数为m
# 那么 m<= n <= m+120 认为提取成功
# 理想参数 depth=5 limitcount=180
# 对照参数 depth 3~11 间隔2; limitcount  100~300 间隔40
# 则对照参数组 为30组
cursor.execute("SELECT html,content FROM main_content_sample")
res = cursor.fetchall()
datas = []
for r in res:
    lines = [line.strip() for line in r[0].splitlines()]
    datas.append((lines, len(r[1])))

results = []
xticklabels = []
success_rate = []
use_time_avg = []
for depth in [3,4,5,6]:
    for limitCount in range(140, 260, 40):
        result = {}
        key = "({0},{1})".format(depth, limitCount)
        result[key] = {}
        count = 0
        all_time = 0.0
        for data in datas:
            content_list = data[0]
            origin_content_len = data[1]
            start = time.time()
            main_content, lines = get_main_content(content_list, limitCount, depth)
            end = time.time()
            use_time = end - start
            all_time += use_time
            if origin_content_len * 0.8 <= len(main_content) <= origin_content_len * 1.4:
                count += 1
        result[key]['提取成功次数'] = count
        result[key]['平均用时'] = round(all_time / len(datas) * 1000, 3)
        results.append(result)
        success_rate.append(count / len(datas))
        use_time_avg.append(round(all_time / len(datas) * 1000, 3))
        xticklabels.append(key)

for temp in results:
    print(temp)

ind = np.arange(len(success_rate))  # the x locations for the groups
width = 0.35  # the width of the bars
plt.rcParams['font.sans-serif'] = ["Microsoft YaHei"]
fig, ax = plt.subplots()
rects1 = ax.bar(ind - width/2, success_rate, width, color='SkyBlue', label='成功率')
rects2 = ax.bar(ind + width/2, use_time_avg, width, color='IndianRed', label='平均用时(ms)')

# Add some text for labels, title and custom x-axis tick labels, etc.
ax.set_ylabel('比率')
ax.set_xlabel('参数组合')
ax.set_title('参数对比')
ax.set_xticks(ind)
ax.set_xticklabels(xticklabels)
ax.legend()


def autolabel(rects, xpos='center'):
    """
    Attach a text label above each bar in *rects*, displaying its height.

    *xpos* indicates which side to place the text w.r.t. the center of
    the bar. It can be one of the following {'center', 'right', 'left'}.
    """

    xpos = xpos.lower()  # normalize the case of the parameter
    ha = {'center': 'center', 'right': 'left', 'left': 'right'}
    offset = {'center': 0.5, 'right': 0.57, 'left': 0.43}  # x_txt = x + w*off

    for rect in rects:
        height = rect.get_height()
        ax.text(rect.get_x() + rect.get_width()*offset[xpos], 1.01*height,
                '{}'.format(height), ha=ha[xpos], va='bottom')


autolabel(rects1, "left")
autolabel(rects2, "right")
plt.savefig('params.png')
plt.show()