# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/spider-middleware.html

import re
from scrapy import signals


class MmjpgSpiderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, dict or Item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Response, dict
        # or Item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class HeadersRefererMiddleware(object):
    """
    为每个request的header设置referer， 要求是当前美女图的 base_url
    :param object:
    :return:
    """
    def __init__(self, crawler):
        self.crawler = crawler

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler)

    def set_referer(self, request):
        """
        http://www.mmjpg.com/mm/311/
        http://img.mmjpg.com/2015/311/10.jpg
        
        :param request: 
        :return: 
        """
        res = re.match("http://img.mmjpg.com/(.*?)/(.*?)/\d+.jpg",request.url)
        uid = res.group(2)
        base_url = "http://www.mmjpg.com/mm/{uid}".format(uid=uid)
        return base_url

    def process_request(self, request, spider):
        if "img" in request.url:
            # 设置Referer
            headers = {
                'Accept': 'image/webp,image/*,*/*;q=0.8',
                'Accept-Encoding': 'gzip, deflate, sdch',
                'Accept-Language': 'zh-CN,zh;q=0.8',
                'Connection': 'keep-alive',
                'Host': 'img.mmjpg.com',
                'Upgrade-Insecure-Requests': '1',
                'Referer': self.set_referer(request),
                'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
            }
            spider.logger.info("========: %s" % request.url)
            request.headers = headers
            spider.custom_settings = {
                'CONCURRENT_REQUESTS_PER_IP': 1,
                'DOWNLOAD_DELAY': 1,
                'RANDOMIZE_DOWNLOAD_DELAY': True
            }

            # request.headers.setdefault('Referer', self.set_referer(request))

            # spider.logger.info("查看request 的 headers：\n %s" % request.headers)
            # spider.logger.info("=======：  %s" %request.url)

    # def process_response(self, request, response, spider):

        # if 'img' in request.url:
        # spider.logger.info("------> response:  {0}: {1}".format(response.status, response.body))

        # return response
