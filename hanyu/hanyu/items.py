# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

from scrapy import Item,Field


class HanyuItem(Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    # 词语名称
    title = Field()
    # 解释
    explain = Field()
    # 词语释义
    chinese_mean = Field()
    # 词语举例
    eg = Field()
    # 近义词/反义词
    synonyms = Field()
