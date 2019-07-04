"""
@date: 2019-07-04
@author: Jiaqiu Jiang
@description: NLP实验2-汉语命名实体自动识别系统
"""

import os
import sys
from preprocessing import Lab2_Preprocessing
from evaluation import Lab2_Evaluation

# 这里定义CRF++的执行文件和训练模板
__CRFPP_LEARN_EXEC__ = '.\\crf++\\crf_learn.exe'
__CRFPP_TEST_EXEC__ = '.\\crf++\\crf_test.exe'
__CRFPP_TEMPL_PATH__ = './crf++/example/seg/template'

# 语料库文件
__CORPUS_FILE__ = './data/peopledaily1998.txt'

# 预处理完毕后训练与测试数据的存放位置
__TRAIN_DATA__ = './data/train.txt'
__TEST_DATA__ = './data/test.txt'

# CRF模型
__MODEL__ = './model/model'

# CRF测试输出文件
__TEST_OUT__ = './out/test_output.txt'


if __name__ == "__main__":

    param = 'all'
    if len(sys.argv) > 1 and sys.argv[1] in ['train', 'test']:
        param = sys.argv[1]

    if param in ['train', 'all']:

        print('********* 数据预处理 *********')
        preprocess = Lab2_Preprocessing()
        preprocess.prepare_data(__CORPUS_FILE__)
        preprocess.generate_data(__TRAIN_DATA__, __TEST_DATA__)
        print('训练数据已保存:', __TRAIN_DATA__)
        print('测试数据已保存:', __TEST_DATA__)

        print('********* CRF模型训练 *********')
        train_cmd = [__CRFPP_LEARN_EXEC__, '-f 3', '-c 1.5',
                     __CRFPP_TEMPL_PATH__, __TRAIN_DATA__, __MODEL__]
        ret_code = os.system(' '.join(train_cmd))
        if ret_code != 0:
            exit(ret_code)
        
    if param in ['test', 'all']:
    
        print('********* CRF模型测试 *********')
        test_cmd = [__CRFPP_TEST_EXEC__, '-m', __MODEL__, __TEST_DATA__,
                    '>>', __TEST_OUT__]
        ret_code = os.system(' '.join(test_cmd))
        if ret_code != 0:
            exit(ret_code)
        evaluation = Lab2_Evaluation()
        p, r, f = evaluation.eval(__TEST_OUT__)
        print('Precision:', p)
        print('Recall:', r)
        print('F1:', f)