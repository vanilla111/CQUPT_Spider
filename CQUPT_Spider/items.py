# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from CQUPT_Spider.models.CquptEsType import CquptType
from CQUPT_Spider.utils.common import get_md5, gen_suggests
from scrapy.loader.processors import TakeFirst, Join, MapCompose
from scrapy.loader import ItemLoader


def default_value(x):
    if x:
        return x
    else:
        return 'None'


class CquptSpiderItemLoader(ItemLoader):
    default_output_processor = TakeFirst()


class CquptSpiderItem(scrapy.Item):
    url = scrapy.Field()
    url_obj_id = scrapy.Field(
        input_processor=MapCompose(get_md5)
    )
    meta_description = scrapy.Field()
    meta_keywords = scrapy.Field()
    html_title = scrapy.Field()
    title = scrapy.Field()
    create_date = scrapy.Field()
    content = scrapy.Field()
    tags = scrapy.Field()
    authors = scrapy.Field()
    top_image = scrapy.Field()
    crawl_time = scrapy.Field()
    crawl_update_time = scrapy.Field()

    def get_insert_sql(self):
        _sql = "INSERT INTO cqupt_search(url, url_obj_id, meta_description, meta_keywords, html_title, title, create_date, content," \
               " tags, authors, top_image, crawl_time) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        params = []
        values = ['url', 'url_obj_id', 'meta_description', 'meta_keywords', 'html_title', 'title', 'create_date',
                  'content', 'tags', 'authors', 'top_image', 'crawl_time']
        for value in values:
            if value in self:
                params.append(self[value])
            else:
                params.append('None')
        return _sql, params

    def save_to_es(self):
        cqupt = CquptType()
        cqupt.url = self['url']
        cqupt.url_obj_id = self['url_obj_id']
        cqupt.title = self['title']
        cqupt.content = self['content']
        if 'top_image' in self:
            cqupt.top_image = self['top_image']
        cqupt.tags = self['tags']
        cqupt.authors = self['authors']
        cqupt.create_date = self['create_date']
        cqupt.suggest = gen_suggests(CquptType.Index.name, ((cqupt.title, 10), (cqupt.tags, 8)))
        cqupt.save()
        return


class UrlItem(scrapy.Item):
    url = scrapy.Field()

    def get_insert_sql(self):
        _sql = "INSERT INTO urls(url) VALUES (%s)"
        params = (self['url'],)
        return _sql, params
