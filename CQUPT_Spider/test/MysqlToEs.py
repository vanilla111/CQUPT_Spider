# -*- coding: utf-8 -*-
import MySQLdb
from elasticsearch import Elasticsearch
from elasticsearch_dsl import connections
from elasticsearch import helpers
from CQUPT_Spider.utils.common import gen_suggests

connections.create_connection(hosts=['localhost'], timeout=30)
es = Elasticsearch()

db = MySQLdb.connect('localhost', 'root', '', 'cqupt', charset='UTF8')
cursor = db.cursor()
cursor.execute('select count(id) from cqupt_search')
nums = cursor.fetchone()[0]
print(nums)

sql = "select * from cqupt_search limit {}, 1000"
print(nums // 1000)
for i in range(0, nums // 1000):
    get_sql = sql.format(i * 1000)
    cursor.execute(get_sql)
    datas = cursor.fetchall()
    bulk_data = []
    for data in datas:
        url = data[1]
        url_obj_id = data[2]
        meta_description = data[3]
        meta_keywords = data[4]
        html_title = data[5]
        title = data[6]
        content = data[7]
        authors = data[8]
        create_date = data[9]
        tags = data[10]
        top_image = data[11]
        crawl_time = data[12]
        es_title = html_title if len(html_title) > len(title) else title
        if tags == 'None': tags = ''
        if tags.startswith('首页,导航,官网'):
            tags = tags[8:]
        tags_set = set()
        for x in tags.split(','):
            tags_set.add(x)
        if meta_keywords != 'None':
            for x in meta_keywords.split(','):
                tags_set.add(x)
        if meta_description != 'None':
            for x in meta_description.split(','):
                tags_set.add(x)
        tags = ','.join(tags_set)
        action = {
            "_index": "cqupt",
            "_type": "html_info",
            "_id": url_obj_id,
            "_source": {
                "url": url,
                "title": es_title,
                "content": None if len(content) < 10 else content,
                "top_image": None if len(top_image) < 10 else top_image,
                "authors": None if authors == 'None' else authors,
                "create_date": crawl_time if create_date == 'None' else None,
                "tags": tags,
                "suggest": gen_suggests('cqupt', ((es_title, 10), (tags, 8)))
            }
        }
        #print(action['source']['tags'])
        bulk_data.append(action)
    #helpers.bulk(es, bulk_data)