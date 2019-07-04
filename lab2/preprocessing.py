"""
@date: 2019-07-04
@author: Jiaqiu Jiang
"""

import re
import random

__DELIM__ = '\t'

class Lab2_Preprocessing:
    def __init__(self):
        self.__data__ = list()

    @staticmethod
    def repl_lword(matched):
        word = re.sub(r'[\[,\],a-z,A-Z,\/, ]', '', matched.group(1))
        pos = matched.group(2)
        return word + '/' + pos

    @staticmethod
    def tag_word(word, entity_type):
        if len(word) == 1:
            return word + __DELIM__ + 'W' + '\n'
        res = ''
        for i, ch in enumerate(word):
            if i == 0:
                prefix = 'B_'
            elif i == len(word) - 1:
                prefix = 'E_'
            else:
                prefix = 'M_'
            tag = (prefix + entity_type)
            res += (ch + __DELIM__ + tag + '\n')
        return res

    
    def prepare_data(self, path, encoding='utf-8'):
        train_file = open(path, 'r', encoding=encoding)
        for row in train_file.readlines():
            if row.strip() == '':
                continue
            # 处理中括号
            row = re.sub(r'(\[.*?\])([a-z,A-Z]+)', self.repl_lword, row)
            row_data = ''
            # 对于不同类别词语做标记
            for raw_word in row.split()[1:]:
                word, pos = raw_word.split('/')
                if pos == 't':     #时间类
                    row_data += self.tag_word(word, 'TIME')
                elif pos == 'ns':  # 地点类
                    row_data += self.tag_word(word, 'LOC')
                elif pos == 'nr':  # 人名类
                    row_data += self.tag_word(word, 'PER')
                elif pos == 'nt':  # 组织团体类
                    row_data += self.tag_word(word, 'ORG')
                else:              # 其他
                    if len(word) == 1:   # 如果是非实体的单字词
                        row_data += (word + __DELIM__ + 'S' + '\n')
                        continue
                    for ch in word:
                        row_data += (ch + __DELIM__ + 'O' + '\n')
            self.__data__.append(row_data)
    
    def split_data(self, ratio=0.8):
        split_idx = int(ratio * len(self.__data__))
        random.shuffle(self.__data__)
        train_data = self.__data__[:split_idx]
        test_data = self.__data__[split_idx:]
        return train_data, test_data
    
    def generate_data(self, train_path, test_path, encoding='utf-8', ratio=0.8):
        train_data, test_data = self.split_data(ratio=ratio)
        with open(train_path, 'w', encoding=encoding) as train_file:
            train_file.write('\n'.join(train_data))
        with open(test_path, 'w', encoding=encoding) as test_file:
            test_file.write('\n'.join(test_data))
    