import re
import math


class Segmentation:
    def __init__(self):
        self.__word_dict__ = dict()      # 词表
        self.__pos_cnt__ = dict()       # 词性总数记录
        self.__transfer_mat__ = dict()   # 转移概率矩阵
        self.__emission_dict__ = dict()  # 发射概率表

    def __add_word__(self, word, pos, count=1):
        # 将词语加入到词表
        if word not in self.__word_dict__.keys():
            self.__word_dict__[word] = dict()
        if pos not in self.__word_dict__[word].keys():
            self.__word_dict__[word][pos] = count
        else:
            self.__word_dict__[word][pos] += count
    
    def __add_pos_cnt__(self, pos, count=1):
        # 记录词性出现数目
        if pos not in self.__pos_cnt__.keys():
            self.__pos_cnt__[pos] = count
        else:
            self.__pos_cnt__[pos] += count

    def __add_transmission__(self, pos1, pos2, count=1):
        # 加入转移概率矩阵
        if pos1 not in self.__transfer_mat__.keys():
            self.__transfer_mat__[pos1] = dict()
        if pos2 not in self.__transfer_mat__[pos1].keys():
            self.__transfer_mat__[pos1][pos2] = count
        else:
            self.__transfer_mat__[pos1][pos2] += count

    def __calc_emission__(self):
        # 计算发射概率矩阵
        for word, pos_dict in self.__word_dict__.items():
            self.__emission_dict__[word] = dict()
            for pos, cnt in pos_dict.items():
                self.__emission_dict__[word][pos] = cnt / self.__pos_cnt__[pos]

    def __calc_transfer__(self):
        # 计算转移概率矩阵
        pos_list = self.__pos_cnt__.keys()
        for pos1 in pos_list:
            for pos2 in pos_list:
                self.__add_transmission__(pos1, pos2, 0)
                self.__transfer_mat__[pos1][pos2] /= self.__pos_cnt__[pos1]

    def train(self, path, encoding='utf-8'):
        self.__word_dict__ = dict()
        train_file = open(path, encoding=encoding)
        # 逐句子处理
        for row in train_file.readlines():
            if row.strip() == '':
                continue
            pos_prev = '<BOS>'  # 每个句子开始时，将前一个词的词性记录为<BOS>
            self.__add_pos_cnt__('<BOS>')
            for raw_word in row.split()[1:]:
                if raw_word[0] == '[':
                    raw_word = raw_word[1:]
                if ']' in raw_word:
                    raw_word = raw_word.split(']')[0]
                word, pos = raw_word.split('/')  # 将词语和词性分开
                self.__add_word__(word, pos)
                self.__add_pos_cnt__(pos)
                self.__add_transmission__(pos_prev, pos)
                pos_prev = pos
            self.__add_pos_cnt__('<EOS>')
            self.__add_transmission__(pos_prev, '<EOS>')
        self.__calc_emission__()
        self.__calc_transfer__()
        train_file.close()

    def __viterbi_pos__(self, words):
        # 正向计算路径概率
        paths = list()
        probs = {'<BOS>': 0}
        for i in range(len(words)):
            t_prob = self.__transfer_mat__
            e_prob = self.__emission_dict__[words[i]]
            path = dict.fromkeys(e_prob.keys(), None)
            
            best_probs = dict()
            for pos in e_prob.keys():
                best_prob = float('-inf')
                best_pre_pos = None
                for pre_pos in probs.keys():
                    # 前一个词的概率*转移概率*当前词的发射概率
                    tmp = probs[pre_pos] + math.log(t_prob[pre_pos][pos]) + \
                          math.log(e_prob[pos])
                    if tmp >= best_prob:
                        best_prob = tmp
                        best_pre_pos = pre_pos
                best_probs[pos] = best_prob
                path[pos] = best_pre_pos
            probs = best_probs
            paths.append(path)

        # 反向回溯找到概率最大的路径
        res = list()
        pos = max(probs, key=probs.get)
        for i in reversed(range(len(paths))):
            res.append(pos)
            pos = paths[i][pos]
        res.reverse()
        return res

    def pos(self, text):
        words = self.cut(text)
        poses = self.__viterbi_pos__(words)
        return words, poses

    def __get_max_length__(self):
        return max(map(len, self.__word_dict__.keys()))

    def __fmm_cut__(self, text):
        res = list()
        wnd_max_size = self.__get_max_length__()
        seg_dict = self.__word_dict__.keys()
        while len(text) > 0:
            wnd_size = min(len(text), wnd_max_size)
            while text[:wnd_size] not in seg_dict and wnd_size > 1:
                wnd_size -= 1
            res.append(text[:wnd_size])
            text = text[wnd_size:]
        return res
    
    def __rmm_cut__(self, text):
        res = list()
        wnd_max_size = self.__get_max_length__()
        seg_dict = self.__word_dict__.keys()
        while len(text) > 0:
            wnd_size = min(len(text), wnd_max_size)
            while text[-wnd_size:] not in seg_dict and wnd_size > 1:
                wnd_size -= 1
            res.append(text[-wnd_size:])
            text = text[:-wnd_size]
        res.reverse()
        return res

    def cut(self, text, method='mixed'):
        if method == 'fmm':
            res = self.__fmm_cut__(text)
        elif method == 'rmm':
            res = self.__rmm_cut__(text)
        else:
            res_fmm = self.__fmm_cut__(text)
            res_rmm = self.__rmm_cut__(text)
            if len(res_fmm) != len(res_rmm):
                res = res_rmm if len(res_rmm) < len(res_fmm) else res_fmm
            elif res_fmm == res_rmm:
                res = res_fmm
            else:
                fmm_s_cnt = len([w for w in res_fmm if len(w) == 1])
                rmm_s_cnt = len([w for w in res_rmm if len(w) == 1])
                res = res_rmm if rmm_s_cnt < fmm_s_cnt else res_fmm
        return res
    
    def save_dict(self, path, encoding='utf-8'):
        rows = list()
        for word, pos_dict in self.__word_dict__.items():
            row = word
            for pos, cnt in pos_dict.items():
                row += (' ' + str(cnt) + ' ' + pos)
            rows.append(row)
        rows.sort()
        dict_file = open(path, 'w', encoding=encoding)
        dict_file.write('\n'.join(rows))
        dict_file.close()

    def load_dict(self, path, encoding='utf-8'):
        self.__word_dict__ = dict()
        dict_file = open(path, encoding=encoding)
        rows = dict_file.read().split('\n')
        for row in rows:
            if row.strip() == '':
                continue
            word, pos_row = row.split(' ', maxsplit=1)
            for cnt_pos in re.findall('[1-9][0-9]* [a-z]+', pos_row):
                cnt, pos = cnt_pos.split()
                self.__add_word__(word, pos, cnt)


if __name__ == "__main__":
    seg = Segmentation()
    seg.train('data/train.txt')
    seg.save_dict('data/dict_1998.txt')
    words, poses = seg.pos('你好呀')
    for word, pos in zip(words, poses):
        print(word+'/'+pos, end=' ')
