import sys
import os
import getopt
import re
import time
import utils
from segmentation3 import Segmentation



def test_cut(seg, path, encoding='utf-8'):
    test_file = open(path, encoding=encoding)
    words_occur_cnt = 0  # 切分出的词语中出现在标准结果中的词语数
    words_cut_cnt = 0    # 分词结果中的切分词语数
    words_norm_cnt = 0   # 标准结果中的切分词语数
    texts = list()
    time_start = time.time()
    for row in test_file.readlines():
        if row.strip() == '':
            continue
        text = re.sub('(/[a-z,A-Z]+)* *', '', row).strip()
        texts.append(text)
        words_cut = seg.cut(text)
        words_norm = list(map(utils.get_word_from_wordpos, row.split()))
        words_cut_cnt += len(words_cut)
        words_norm_cnt += len(words_norm)
        words_occur_cnt += len([1 for word in words_cut if word in words_norm])
    precision_rate = words_occur_cnt / words_cut_cnt
    recall_rate = words_occur_cnt / words_norm_cnt
    cutword_speed = utils.get_filesize(path) / (time.time() - time_start)
    print("精确率:", precision_rate)
    print("召回率:", recall_rate)
    print("分词速度:", cutword_speed, 'KB/s')


def test_pos(seg, path, encoding='utf-8'):
    test_file = open(path, encoding=encoding)
    total_pos_cnt = 0
    true_pos_cnt = 0
    for row in test_file.readlines():
        if row.strip() == '':
            continue
        words = re.sub('/[a-z,A-Z]+', '', row).strip().split()
        poses_norm = re.sub('[^\x00-\xff]*/', '', row).strip().split()
        poses_tag = seg.pos_cutted(words)
        total_pos_cnt += len(poses_norm)
        true_pos_cnt += len([1 for i in range(len(poses_norm)) if poses_norm[i] == poses_tag[i]])
    true_rate = true_pos_cnt / total_pos_cnt
    print("正确率:", true_rate)


if __name__ == "__main__":
    # generate_test_file('data/train.txt', 'data/test.txt')
    seg = Segmentation()
    # seg.train('data/train.txt')
    # seg.save('model/model.json')
    seg.load('model/model.json')
    # words, poses = seg.pos('今天天气非常的好')
    # for word, pos in zip(words, poses):
    #     print(word + '/' + pos, end=' ')
    print('********* 人民日报1998测试集 *********')
    test_cut(seg, 'data/test.txt')
    print('********* 北大分词测试集 *********')
    test_cut(seg, 'data/pku_test_gold.utf8')
    print('********* MSR分词测试集 *********')
    test_cut(seg, 'data/msr_test_gold.utf8')
    print('********* 词性标注测试 *********')
    test_pos(seg, 'data/test.txt')
    