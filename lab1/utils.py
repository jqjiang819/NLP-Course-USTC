import os
import random

def generate_test_file(in_path, out_path, encoding='utf-8'):
    train_file = open(in_path, encoding=encoding)
    test_file = open(out_path, 'w', encoding=encoding)
    for row in train_file.readlines():
        if row.strip() == '':
            continue
        if random.random() > 0.15:
            continue
        new_words = list()
        for raw_word in row.split()[1:]:
            if raw_word[0] == '[':
                word = raw_word[1:]
            elif ']' in raw_word:
                word = raw_word.split(']')[0]
            else:
                word = raw_word
            new_words.append(word)
        test_file.write(' '.join(new_words) + '\n')
    test_file.close()

def get_word_from_wordpos(wordpos):
    return wordpos.split('/')[0]

def get_filesize(path):
    fsize = os.path.getsize(path)
    fsize = fsize / 1024.0
    return round(fsize, 2)