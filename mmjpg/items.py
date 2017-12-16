# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy import Item, Field

class MmjpgItem(Item):
    url = Field()
    title = Field()
    publish_date = Field()
    mm_image_url = Field()
    looked = Field()
    like = Field()

