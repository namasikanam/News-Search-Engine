import os
import json
import jieba
import jieba.analyse as analyse
import jieba.posseg as pseg

# 这个东西是我以后要dump的
segs = []

# 搞点事情


def filt(a):
    return list(filter(lambda x: pseg.lcut(x)[0].flag not in {'x'}, a))


# 首先我要得到news这个文件下的所有文件
counter = 0
for filename in os.listdir('./news'):
    # 读入json
    with open(os.path.join('./news', filename), 'r', encoding='utf-8') as file:
        # debug信息
        counter += 1
        if counter % 10 == 0:
            print("====Start work with {}:{}===".format(counter, filename))

        # 读入
        news = json.load(file)
        # 下面开始分词
        # 注意词性过滤(不用注意了...)
        seg = {'id': news['id']}
        # title直接来分
        # print(jieba.lcut_for_search(news['title']))
        seg['title'] = list(filter(lambda x: pseg.lcut(x)[0].flag not in {
                            'x'}, jieba.lcut_for_search(news['title'])))
        # body搞一下, 默认的topKey=20
        seg['body'] = list(filter(lambda x: pseg.lcut(x[0])[0].flag not in {'x'}, analyse.extract_tags(
            ''.join(news['body']), withWeight=True)))

        # debug信息
        if counter % 100 == 0:
            print(seg)
        # 搞完了
        segs.append(seg)

with open('./segmentation.json', 'w') as file:
    json.dump(segs, file, ensure_ascii=False, indent=1)
