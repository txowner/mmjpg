# _*_ coding:utf8 _*_

import os
import sys
from scrapy.cmdline import execute

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

if __name__ == "__main__":
    execute(["scrapy", "crawl", "meizi"])