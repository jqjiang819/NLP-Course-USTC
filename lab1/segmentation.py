

class Segmentation:
    def __init__(self, path, encoding='utf-8'):
        dict_file = open(path, encoding=encoding)
        self.__words__ = dict_file.read().split()
        self.__construct_index__(self.__words__)
        
    def __construct_index__(self, words):
        htable = dict()
        htable[words[0][0]] = [0, -1]
        for i in range(1, len(words)):
            if words[i][0] != words[i-1][0]:
                htable[words[i-1][0]][1] = i
                htable[words[i][0]] = [i, -1]
        htable[words[len(words)-1][0]][1] = len(words)
        self.__htable__ = htable

    def __get_dict__(self, first_char=''):
        if first_char == '':
            res_array = self.__words__
        else:
            idx = self.__htable__[first_char]
            res_array = self.__words__[idx[0]:idx[1]]
        return res_array

    def __get_dict_max_len__(self):
        return max(map(len, self.__words__))

    def __fmm_cut__(self, text):
        res = list()
        while len(text) > 0:
            tmp_dict = self.__get_dict__(text[0])
            wnd_size = min(len(text), max(map(len, tmp_dict)))
            while text[:wnd_size] not in tmp_dict and wnd_size > 1:
                wnd_size -= 1
            res.append(text[:wnd_size])
            text = text[wnd_size:]
        return res

    def __rmm_cut__(self, text):
        res = list()
        wnd_max_size = self.__get_dict_max_len__()
        while len(text) > 0:
            wnd_size = min(len(text), wnd_max_size)
            while text[-wnd_size:] not in self.__get_dict__(text[-wnd_size]) and wnd_size > 1:
                wnd_size -= 1
            res.append(text[-wnd_size:])
            text = text[:-wnd_size]
        res.reverse()
        return res

    def cut(self, text, method='mixed'):
        if method == 'fmm':
            res = self.__fmm_cut__(text)
        if method == 'rmm':
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
