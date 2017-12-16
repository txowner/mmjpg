# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import json
import logging
import pymongo
import redis
from scrapy.pipelines.images import *

#下载图片后把本地图片地址和数据库中item对应
# class ArticleImagePipeline(ImagesPipeline):
#     """
#     继承并重载下载封面图的Pipeline的部分功能
#     """
#     def item_completed(self, results, item, info):
#         if "mm_image_url" in item:
#             image_file_path = ''
#             for ok, value in results:
#                 if ok:
#                     image_file_path = value["path"]
#             item["mm_image_url"] = image_file_path
#
#         return item


class SaveToMongoDBPipeline(object):
    """
    将接收到的item数据集保存到MongoDB
    """

    def __init__(self, mongo_uri, mongo_db, mongo_user, mongo_passwd):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db
        self.mongo_user = mongo_user
        self.mongo_passwd = mongo_passwd

    # 目前感觉用起来和from_crawler效果一样
    @classmethod
    def from_settings(cls, settings):
        mongo_uri = settings["MONGO_URI"]
        mongo_db = settings["MONGO_DB"]
        mongo_user = settings["MONGO_USER"]
        mongo_passwd = settings["MONGO_PASSWD"]
        return cls(mongo_uri, mongo_db, mongo_user, mongo_passwd)

    def open_spider(self, spider):
        """ 
        open_spider 方法是在这个spider(或则scrapy启动)启动的时候就调用
        """
        self.redis_cli = redis.Redis(host='127.0.0.1', port=6379, password='tianxuroot')

        self.client = pymongo.MongoClient(self.mongo_uri)
        self.client['admin'].authenticate(self.mongo_user, self.mongo_passwd)
        self.db = self.client[self.mongo_db]
        # logger = logging.getLogger("SaveMongoPipeline")  # 指定logger的名字
        logger = logging.getLogger(__name__)  # 指定logger的名字为当前模块
        logger.info("MongoDB 身份验证通过")  # 打印哪种等级的消息

    def close_spider(self, spider):
        self.client.close()

    def process_url(self, url_list):
        return url_list[0]

    def process_title(self, title):
        if "(" in title:
            title = title[:title.index('(')]
        return title

    def process_item(self, item, spider):
        collection_name = item.__class__.__name__
        # self.db[collection_name].insert(dict(item))   # 这里直接插入不好，为防止重复，用update更好，没有就插入，有就更新
        item['mm_image_url'] = self.process_url(item['mm_image_url'])
        item['title'] = self.process_title(item['title'])

        # 在redis中生成集合中的每一项是一个元组， 包含 组名字 和url
        tm = (item["title"], item["mm_image_url"])
        self.redis_cli.sadd('mm_tm', json.dumps(tm))

        self.db[collection_name].update({'mm_image_url': item['mm_image_url']}, {'$set': item}, True)
        # update 第一个参数是判断条件，是否存在， 第二个参数是要更新的item，键名固定， 第三个参数为True表示存在就更新，不存在就插入

        return item

# class MyImageDownloadPipeline(ImagesPipeline):
#     """
#     扩展自带的图片下载，自己实现简单的图片下载器
#     """
#     def __init__(self, headers, store_uri, *args, **kwargs):
#         super(MyImageDownloadPipeline, self).__init__(store_uri,*args, **kwargs)
#         self.headers = headers
#
#     @classmethod
#     def from_crawler(cls, crawler):
#         return cls(
#             headers=crawler.settings.get("DEFAULT_REQUEST_HEADERS")
#         )
#
#     def get_media_requests(self, item, info):
#         self.headers['Referer'] = item['url']
#         return [Request(url=x, headers=self.headers) for x in item.get(self.images_urls_field, [])]
