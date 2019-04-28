from django.shortcuts import render
from django.http import HttpResponse
import jieba
import jieba.posseg as pseg
import json
import time
import datetime
import os.path
import re

# Create your views here.


def digest(newsId):  # 给我一个id, 我会告诉你: id, title, digest. 没啦!
    with open(os.path.join('news/', newsId+'.json'), 'r', encoding='utf-8') as file:
        news = json.load(file)
    news['digest'] = ''.join(map(lambda x: x.strip(), news['body']))
    if len(news['digest']) > 200:
        news['digest'] = news['digest'][:200]+'...'
    news.pop('body')
    return news


def search(request):
    # 计时器启动!
    startTime = time.time()

    # Parse URL
    q = request.GET.get('q')
    fromTime = request.GET.get('from')
    toTime = request.GET.get('to')
    page = request.GET.get('page')

    # 计算, 并根据duration排除
    rawWords = set(filter(lambda x: pseg.lcut(x)[0].flag not in {
        'x'}, jieba.lcut_for_search(q)))
    words = {}
    for word in rawWords:
        if word in words:
            words[word] += 1
        else:
            words[word] = 1

    # print(words)

    with open('segmentation.json', 'r', encoding='utf-8') as file:
        data = json.load(file)
    news = list(map(lambda news: {
        'id': news['id'],
        'value': (
            sum(map(lambda title: words.get(title, 0), news['title'])),
            sum(map(lambda body: words.get(body[0], 0)*body[1], news['body'])),
        )
    }, data))
    news.sort(key=lambda x: x['value'], reverse=True)

    # print(list(filter(lambda new: sum(new['value']), news))[:20])

    news = map(digest, list(
        map(lambda x: x['id'], filter(lambda new: sum(new['value']), news))))

    try:
        ldt = datetime.datetime.strptime(fromTime, "%Y.%m.%d")
    except:
        ldt = datetime.datetime(1, 1, 1)
    try:
        rdt = datetime.datetime.strptime(toTime, "%Y.%m.%d")
    except:
        rdt = datetime.datetime(3000, 1, 1)

    def checkDatetime(news):
        # print(news['time'])
        dt = datetime.datetime(
            *map(lambda x: int(x), re.findall(r'\d+', news['time'])[:3]))
        return ldt <= dt and dt <= rdt
    news = filter(checkDatetime, news)
    news = list(news)

    totalPage = (len(news)+9)//10
    if page:
        firstSearch = False
    else:
        firstSearch = True
        page = 1
    page = int(page)
    return render(request, 'engine/search.njk', {
        'q': q,
        'fromTime': fromTime,
        'toTime': toTime,
        'costTime': time.time() - startTime,
        'total': len(news),
        'totalPage': totalPage,
        'page': page,
        'firstSearch': firstSearch,
        'news': news[(page - 1) * 10:page * 10],
        'words': rawWords,
    })


def index(request):
    news = list(
        map(digest, map(lambda s: s.split('.')[0], os.listdir('./news'))))
    totalPage = (len(news)+9)//10
    page = request.GET.get('page')
    if page == None:
        page = 1
    page = int(page)
    return render(request, 'engine/index.njk', {
        'page': page,
        'totalPage': totalPage,
        'news': news[(page - 1) * 10:page * 10],
        'totalNews': len(news),
    })


def detail(request, id):
    with open(os.path.join('./news', id+'.json')) as file:
        article = json.load(file)

    rawWords = set(filter(lambda x: pseg.lcut(x)[0].flag not in {
        'x'}, jieba.lcut_for_search(article['title'])))
    words = {}
    for word in rawWords:
        if word in words:
            words[word] += 1
        else:
            words[word] = 1

    # print('detail.words={}'.format(words))

    with open('segmentation.json', 'r', encoding='utf-8') as file:
        data = json.load(file)
    news = list(map(lambda new: {
        'id': new['id'],
        'value': (
            sum(map(lambda title: words.get(title, 0), new['title'])),
            sum(map(lambda body: words.get(body[0], 0)*body[1], new['body'])),
        )
    }, data))
    news.sort(key=lambda x: x['value'], reverse=True)
    news = list(filter(lambda new: new['id'] != id, news))

    def openJson(id):
        with open(os.path.join('news/', id + '.json'), 'r', encoding='utf-8') as file:
            data = json.load(file)
        return data
    recommends = list(map(lambda x: openJson(x['id']), news[:3]))

    return render(request, 'engine/detail.njk', {
        'article': article,
        'recommends': recommends,
    })
