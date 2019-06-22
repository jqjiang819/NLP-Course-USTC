import math
import json


class Segmentation:
    def __init__(self):
        self.__pos_cnt__ = dict()       # 词性总数记录
        self.__transition__ = dict()    # 转移概率矩阵
        self.__emission__ = dict()      # 发射概率表

    def __add_word__(self, word, pos, count=1):
        # 将词语加入到词表
        if word not in self.__emission__.keys():
            self.__emission__[word] = dict()
        if pos not in self.__emission__[word].keys():
            self.__emission__[word][pos] = count
        else:
            self.__emission__[word][pos] += count
    
    def __add_pos_cnt__(self, pos, count=1):
        # 记录词性出现数目
        if pos not in self.__pos_cnt__.keys():
            self.__pos_cnt__[pos] = count
        else:
            self.__pos_cnt__[pos] += count

    def __add_transition__(self, pos1, pos2, count=1):
        # 加入转移概率矩阵
        if pos1 not in self.__transition__.keys():
            self.__transition__[pos1] = dict()
        if pos2 not in self.__transition__[pos1].keys():
            self.__transition__[pos1][pos2] = count
        else:
            self.__transition__[pos1][pos2] += count

    def __calc_emission__(self):
        # 计算发射概率矩阵
        for word in self.__emission__.keys():
            for pos in self.__emission__[word].keys():
                self.__emission__[word][pos] /= self.__pos_cnt__[pos]

    def __calc_transition(self):
        # 计算转移概率矩阵
        pos_list = self.__pos_cnt__.keys()
        for pos1 in pos_list:
            for pos2 in pos_list:
                self.__add_transition__(pos1, pos2, 0)   # 补齐矩阵中的0（防止由于key不存在而导致的exception）
                self.__transition__[pos1][pos2] /= self.__pos_cnt__[pos1]

    def train(self, path, encoding='utf-8'):
        train_file = open(path, encoding=encoding)
        # 逐句子处理
        for row in train_file.readlines():
            if row.strip() == '':
                continue
            pos_prev = '<BOS>'  # 每个句子开始时，将前一个词的词性记录为<BOS>
            for raw_word in row.split()[1:]:
                # 处理掉“[”和“]”
                if raw_word[0] == '[':
                    raw_word = raw_word[1:]
                if ']' in raw_word:
                    raw_word = raw_word.split(']')[0]
                word, pos = raw_word.split('/')  # 将词语和词性分开
                self.__add_word__(word, pos)     # 将词语加入计数表
                self.__add_pos_cnt__(pos)        # 将该词性的计数加1
                self.__add_transition__(pos_prev, pos) # 增加从上一个词到当前词的词性转换计数
                pos_prev = pos
            # 每一行句子都会有一个<BOS>和<EOS>
            self.__add_pos_cnt__('<BOS>')
            self.__add_pos_cnt__('<EOS>')
            # 添加最后一个词到<EOS>的转移
            self.__add_transition__(pos_prev, '<EOS>')
        # 计算最终的转移概率和发射概率
        self.__calc_emission__()
        self.__calc_transition()
        train_file.close()

    def __viterbi_pos__(self, words):
        # 正向计算路径概率
        paths = list()
        probs = {'<BOS>': 0}
        for i in range(len(words)):
            t_prob = self.__transition__
            e_prob = self.__emission__[words[i]]
            path = dict.fromkeys(e_prob.keys(), None)
            
            best_probs = dict()
            for pos in e_prob.keys():
                best_prob = float('-inf')
                best_pre_pos = None
                for pre_pos in probs.keys():
                    # 前一个词的概率*转移概率*当前词的发射概率
                    try:
                        tmp = probs[pre_pos] + math.log(t_prob[pre_pos][pos]) + \
                              math.log(e_prob[pos])
                    except ValueError:
                        tmp = float('-inf')
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
    
    def pos_cutted(self, words):
        return self.__viterbi_pos__(words)

    def __get_max_length__(self):
        # 获取词典中最长词的长度
        return max(map(len, self.__emission__.keys()))

    def __fmm_cut__(self, text):
        # 正向最大匹配
        res = list()
        wnd_max_size = self.__get_max_length__()     # 取得最大词语长度备用
        seg_dict = self.__emission__.keys()          # 取得词表
        while len(text) > 0:
            wnd_size = min(len(text), wnd_max_size)  # 取词窗口长度不能大于当前语句串长度
            while text[:wnd_size] not in seg_dict and wnd_size > 1:
                wnd_size -= 1                        # 如果词典匹配不到则匹配长度减1重试
            res.append(text[:wnd_size])              # 匹配成功后放入分词结果列表
            text = text[wnd_size:]                   # 截断已匹配的词语
        return res
    
    def __rmm_cut__(self, text):
        # 逆向最大匹配
        res = list()
        wnd_max_size = self.__get_max_length__()
        seg_dict = self.__emission__.keys()
        while len(text) > 0:
            wnd_size = min(len(text), wnd_max_size)
            while text[-wnd_size:] not in seg_dict and wnd_size > 1:
                wnd_size -= 1
            res.append(text[-wnd_size:])
            text = text[:-wnd_size]
        res.reverse()          # 逆向匹配出来的结果方向是反的
        return res

    def cut(self, text, method='mixed'):
        if method == 'fmm':
            res = self.__fmm_cut__(text)
        elif method == 'rmm':
            res = self.__rmm_cut__(text)
        else:
            # 结合正向最大匹配和逆向最大匹配
            res_fmm = self.__fmm_cut__(text)
            res_rmm = self.__rmm_cut__(text)
            # 词语序列长度不等时选择词语数量较少的划分（语义单元越少越好）
            if len(res_fmm) != len(res_rmm):
                res = res_rmm if len(res_rmm) < len(res_fmm) else res_fmm
            # 两种匹配结果相同时没有歧义
            elif res_fmm == res_rmm:
                res = res_fmm
            # 两种匹配词语数相同时，单字字典词数越少越好
            else:
                fmm_s_cnt = len([w for w in res_fmm if len(w) == 1])
                rmm_s_cnt = len([w for w in res_rmm if len(w) == 1])
                res = res_rmm if rmm_s_cnt < fmm_s_cnt else res_fmm
        return res

    def save(self, path):
        model_dict = {
            'pos_count': self.__pos_cnt__,
            'emission': self.__emission__,
            'transition': self.__transition__
        }
        json.dump(model_dict, open(path, 'w'))

    def load(self, path):
        model_dict = json.load(open(path))
        self.__pos_cnt__ = model_dict['pos_count']
        self.__emission__ = model_dict['emission']
        self.__transition__ = model_dict['transition']
