
import os
import re
import time

import redis
import json
import requests


def set_referer(url):
    """
    http://www.mmjpg.com/mm/311/
    http://img.mmjpg.com/2015/311/10.jpg
    """
    res = re.match("http://img.mmjpg.com/(.*?)/(.*?)/\d+.jpg",url)
    uid = res.group(2)
    base_url = "http://www.mmjpg.com/mm/{uid}".format(uid=uid)
    return base_url


def get_tuple_from_redis():
    if redis_cli.scard('mm_tm') >0:
        tm = redis_cli.spop('mm_tm').decode('utf-8')
        # print(tm,  type(tm))
        title, url = json.loads(tm)
        if title.strip().endswith('('):
            title = title.strip("(")
        return title, url
    else:
        print("Not more...")
        return None


def save_images(title, url, content):
    dir_path = 'images/%s' %title
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)

    file_name = dir_path + '/' + url.split("/", 3)[-1].replace('/','')
    with open(file_name, 'wb') as f:
        f.write(content)


def download_images(title, url):
    global image_num
    
    headers = {
        'Accept': 'image/webp,image/*,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, sdch',
        'Accept-Language': 'zh-CN,zh;q=0.8',
        'Connection': 'keep-alive',
        'Host': 'img.mmjpg.com',
        'Upgrade-Insecure-Requests': '1',
        'Referer': set_referer(url),
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
    }
    
    try:
        print("\ndownloading the {0} mm...    url: {1}".format(image_num, url), end='\t')
        # print(headers)
        response = requests.get(url, headers=headers)
        if response.status_code in [200, 201]:
            image_num +=1
            try:
                save_images(title, url, response.content)
                print('ok', end='\t')
                return True
            except Exception:
                print("Generate img error... ")

                # 如果在保存完成之前下载失败， 当前url会再次加到 redis 请求集合中取
                tm = (title, url)
                redis_cli.sadd('mm_tm', json.dumps(tm))
                return False

    except Exception:
        download_images(title, url)


def main():
    title, url = get_tuple_from_redis()
    if url:
        for i in range(3):
            content = download_images(title, url)
            if content: break


if __name__ == '__main__':
    image_num = 0
    redis_cli = redis.Redis(host='127.0.0.1', port=6379, password='tianxuroot')
    # redis_cli = redis.Redis(host='183.222.172.148', port=6379, password='tianxuroot')

    # urls_num = redis_cli.scard('mm_tm')
    # print(urls_num)
    # for i in range(urls_num):
    #     main()
    #     # time.sleep(1)
    while True:
        if redis_cli.scard('mm_tm') > 0:
            main()
        else:
            print("Download Completed")
            break

