# 现在我要来写一个爬虫
# 它会爬一些网站, 并把得到的结果以json格式存在/news/文件夹中.
# 网页存储的名称格式是ID.json, ID使用我得到它的时间.

from urllib.request import Request, urlopen
from urllib.parse import urlencode, urljoin, urlparse
from urllib.error import HTTPError, URLError
from html.parser import HTMLParser
from heapq import heapify,  heappush, heappop
from time import sleep
import random
import datetime
import json
import os
import re
from IPython.core.debugger import Tracer
import hashlib
debug_here = Tracer()

# 先来做一些预处理工作


init_urls = ['http://www.xinhuanet.com/']

# 这里我使用一个heap来存我尚未走过的所有URL, 用一个set来存我走过的所有URL.
heap = list(map(lambda url: (random.random(), url), init_urls))
heapify(heap)
vsted = set()

user_agent = "Robot for assignment, Tsinghua University"
headers = {'User-Agent': user_agent}

# HTML Parser


class MyHTMLParser(HTMLParser):
    def __init__(self, cururl):
        HTMLParser.__init__(self)
        self.tg = self.title = self.time = ""
        self.body = []
        self.cururl = cururl

    def handle_starttag(self, tag, attrs):
        self.tg = tag
        if tag == "a":
            for name, body in attrs:
                if name == "href":
                    desturl = urljoin(cururl, body)
                    if desturl not in vsted:
                        flag = False
                        dst = urlparse(desturl)
                        tp = ""
                        if len(dst[2].split('/')) > 1:
                            tp = dst[2].split('/')[1]
                        for url in init_urls:
                            flag |= urlparse(
                                url)[1] == dst[1] and tp != 'video' and tp != 'photo' and tp != 'company'
                        if flag:
                            heappush(heap, (random.random(), desturl))
                    break
        elif len(attrs) > 0 and (attrs[0][1] == "h-time" or attrs[0][1] == "time"):
            self.tg = "h-time"

    def handle_endtag(self, tag):
        self.tg = ""

    def handle_data(self, data):
        if self.tg == "p":
            self.body.append(data)
        elif self.tg == "title":
            self.title = data.strip()
        elif self.tg == "h-time":
            self.time = data.strip()
# 再来爬


record = 0

for T in range(10 ** 100):
    try:
        # 在下先睡为敬
        sleep(1)

        # 先把网页上的内容都爬下来

        print('========Start {}========'.format(T))

        cururl = heap[0][1]
        heappop(heap)
        req = Request(cururl, headers=headers)
        vsted.add(cururl)

        print("Try ", cururl)

        response = urlopen(req, timeout=10)

        # 让我们来解决编码问题
        page = response.read()
        try:
            page = page.decode('utf-8')
        except UnicodeDecodeError:
            try:
                page = page.decode('GBK')
            except UnicodeDecodeError:
                page = page.decode('GB2312')

        # 再来解析这个家伙
        parser = MyHTMLParser(cururl)
        parser.feed(page)

        if parser.time and parser.body:
            record += 1
            id = hashlib.md5(
                (parser.time + parser.title).encode('utf-8')).hexdigest()

            print("record={}\nid={}\ntitle={}\ntime={}\n".format(
                record, id, parser.title, parser.time))
            with open(os.path.join('./news/', str(id) + '.json'), 'w') as f:
                json.dump({
                    "id": id,
                    "title": parser.title,
                    "time": parser.time,
                    "body": parser.body
                }, f, ensure_ascii=False, indent=1)
            if id == 10000:
                exit(0)

        print('Now I have {} urls to crawl.'.format(len(heap)))
    except:
        continue
