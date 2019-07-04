"""
@date: 2019-07-04
@author: Jiaqiu Jiang
"""

__T_PRE__ = ['B', 'M', 'E', 'W']


class Lab2_Evaluation:
    def __init__(self):
        self.__ENT_DATASET__ = 0   # 数据集中实体计数
        self.__ENT_PREDICT__ = 0   # 预测的实体计数
        self.__ENT_TRUE__ = 0      # 预测正确的实体计数
        pass

    def eval_label(self, eval_path, encoding='utf-8'):
        eval_file = open(eval_path, encoding=encoding)
        for row in eval_file.readlines():
            if row.strip() == '':
                continue
            _, tag, predict_tag = row.split()
            if tag[0] in __T_PRE__:
                self.__ENT_DATASET__ += 1
            if predict_tag[0] in __T_PRE__:
                self.__ENT_PREDICT__ += 1
                if tag == predict_tag:
                    self.__ENT_TRUE__ += 1
        precision = self.__ENT_TRUE__ / self.__ENT_PREDICT__
        recall = self.__ENT_TRUE__ / self.__ENT_DATASET__
        f1 = 2 * (precision * recall) / (precision + recall)
        return precision, recall, f1

    def eval(self, eval_path, encoding='utf-8'):
        eval_file = open(eval_path, encoding=encoding)
        flag_true = 0
        for row in eval_file.readlines():
            if row.strip() == '':
                continue
            _, tag, predict_tag = row.split()
            # 按实体统计
            if tag[0] == 'W':
                self.__ENT_DATASET__ += 1
                if tag == predict_tag:
                    self.__ENT_TRUE__ += 1
            elif tag[0] in ['B', 'M', 'E']:
                if tag[0] == 'B':
                    flag_true = 1
                if tag != predict_tag:
                    flag_true = 0
                if tag[0] == 'E':
                    self.__ENT_DATASET__ += 1
                    if flag_true == 1:
                        self.__ENT_TRUE__ += 1
                        flag_true = 0
            if predict_tag[0] == 'W':
                self.__ENT_PREDICT__ += 1
            elif predict_tag[0] == 'E':
                self.__ENT_PREDICT__ += 1
        precision = self.__ENT_TRUE__ / self.__ENT_PREDICT__
        recall = self.__ENT_TRUE__ / self.__ENT_DATASET__
        f1 = 2 * (precision * recall) / (precision + recall)
        return precision, recall, f1
