# -*- coding: utf-8 -*-
import datetime

from scrapy.spiders import Rule
from scrapy.linkextractors import LinkExtractor
from scrapy_redis.spiders import RedisCrawlSpider
from CQUPT_Spider.items import CquptSpiderItemLoader, CquptSpiderItem
from goose3 import Goose
from goose3.text import StopWordsChinese


class ExplorerSpider(RedisCrawlSpider):
    name = 'explorer'
    redis_key = 'explorer:start_urls'

    rules = (
        Rule(LinkExtractor(canonicalize=True, allow_domains='cqupt.edu.cn', deny=r'^.*(english|korea).cqupt.edu.cn'),
             callback='parse_detail', follow=True),
    )

    main_content_min_length = 180

    def parse_detail(self, response):
        # 学术讲座 http://www.cqupt.edu.cn/cqupt/news_detail.shtml?id=155176964575282691
        # 列表 API http://www.cqupt.edu.cn/getPublicPage.do 外加参数 cookie
        # js 动态加载，详情API http://www.cqupt.edu.cn/getPublicNotic.do?id=155176964575282691
        item_loader = CquptSpiderItemLoader(item=CquptSpiderItem(), response=response)
        g = Goose({'stopwords_class': StopWordsChinese})
        content = g.extract(raw_html=response.text)
        item_loader.add_value('url', response.url)
        item_loader.add_value('url_obj_id', response.url)
        item_loader.add_xpath('html_title', '/html/head/title/text()')
        item_loader.add_value('crawl_time', datetime.datetime.now())
        if len(content.cleaned_text) < self.main_content_min_length:
            # 正文长度不够，认为是导航页或者列表页
            # 尝试解析SEO 信息
            item_loader.add_xpath('meta_description', "/html/head/meta[@name='description']/@content")
            item_loader.add_xpath('meta_keywords', "/html/head/meta[@name='keywords']/@content | "
                                                   "/html/head/meta[@name='Keywords']/@content")
            item_loader.add_value('tags', content.title)
        else:
            item_loader.add_value('meta_keywords', content.meta_keywords)
            item_loader.add_value('meta_description', content.meta_description)
            item_loader.add_value('title', content.title)
            item_loader.add_value('create_date', content.publish_date)
            item_loader.add_value('authors', content.authors)
            item_loader.add_value('top_image', content.top_image)
            item_loader.add_value('tags', content.tags)
            item_loader.add_value('content', content.cleaned_text)
        item = item_loader.load_item()
        return item