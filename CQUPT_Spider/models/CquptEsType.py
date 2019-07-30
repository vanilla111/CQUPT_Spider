# -*- coding: utf-8 -*-
from datetime import datetime
from elasticsearch_dsl import Document, Date, Nested, Boolean, analyzer, InnerDoc, Completion, Keyword, Text, Integer
from elasticsearch_dsl import connections

connections.create_connection(hosts=["localhost"])


class CquptType(Document):
    suggest = Completion(analyzer='ik_max_word')
    title = Text(analyzer='ik_max_word')
    create_date = Date()
    url = Keyword()
    url_obj_id = Keyword()
    top_image = Keyword()
    tags = Text(analyzer='ik_max_word')
    content = Text(analyzer='ik_max_word')
    authors = Keyword()

    class Index:
        name = 'cqupt'

    class Meta:
        doc_type = 'html_info'


if __name__ == '__main__':
    CquptType.init()