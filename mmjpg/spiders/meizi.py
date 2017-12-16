# -*- coding: utf-8 -*-
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from items import MmjpgItem



class MeiziSpider(CrawlSpider):
    name = 'meizi'
    allowed_domains = ['www.mmjpg.com', 'img.mmjpg.com']
    start_urls = ['http://www.mmjpg.com/']

    rules = (
        Rule(LinkExtractor(allow=r'home/\d+$'), follow=True),
        Rule(LinkExtractor(allow=r'mm/\d+$'), callback='parse_item', follow=True),
        Rule(LinkExtractor(allow=r'mm/\d+/\d+$'), callback='parse_item', follow=True),
    )

    def parse_item(self, response):
        url = response.url
        title = response.xpath('//div[@class="article"]/h2/text()').extract_first('')
        publish_date = response.xpath('//div[@class="info"]/i/text()')[0].re(".*?:(.*)")[0].strip()
        looked = response.xpath('//div[@class="info"]/i/text()').re("人气\((\d+)\)")[0].strip()
        like = response.xpath('//div[@class="info"]/i/text()').re("喜欢\((\d+)\)")[0].strip()
        mm_image_url = response.xpath("//div[@id='content']/a/img/@src").extract()  # 下载图片的url字段必须是可以迭代对象

        m_item = MmjpgItem()
        for field in m_item.fields:
            m_item[field] = eval(field)

        yield m_item

    # def closed(self, reason):
    #     """
    #     关闭 selenium 打开的chrome
    #     :param reason:
    #     :return:
    #     """
    #     self.logger.info("关闭browser")
    #     self.browser.close()