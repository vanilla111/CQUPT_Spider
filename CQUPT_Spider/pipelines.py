# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
from twisted.enterprise import adbapi
import MySQLdb
import MySQLdb.cursors


class CquptSpiderPipeline(object):
    def process_item(self, item, spider):
        return item


class MysqlTwistedPipeline(object):

    def __init__(self, pool):
        self.dbpool = pool

    @classmethod
    def from_settings(cls, settings):
        dbinfo = dict(
            host=settings['MYSQL_HOST'],
            user=settings['MYSQL_USER'],
            passwd=settings['MYSQL_PASSWORD'],
            port=settings['MYSQL_PORT'],
            db=settings['MYSQL_DBNAME'],
            charset='utf8',
            cursorclass=MySQLdb.cursors.DictCursor,
            use_unicode=True
        )
        dbpool = adbapi.ConnectionPool("MySQLdb", **dbinfo)
        return cls(dbpool)

    def process_item(self, item, spider):
        # 使用twisted将mysql插入变为异步插入
        query = self.dbpool.runInteraction(self.do_insert, item)
        query.addErrback(self.handle_error, item, spider)

    def do_insert(self, cursor, item):
        # 执行具体的插入
        # 根据不同的item生成不同的sql
        _sql, params = item.get_insert_sql()
        cursor.execute(_sql, params)

    def handle_error(self, failure, item, spider):
        # 处理异步插入的异常
        print(failure)


class ElasticsearchPipeline(object):
    def process_item(self, item, spider):
        item.save_to_es()
        return item