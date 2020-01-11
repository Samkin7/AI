import numpy as np
#导入numpy，类传入对象
class WordSequence(object):

    PAD_TAG = '<pad>' #
    UNK_TAG = '<unk>' #未知标签
    START_TAG = '<s>' #开始标记
    END_TAG = '</s>'  #结束标记

    PAD = 0
    UNK = 1
    START = 2
    END = 3
    #类的初始化
    def __init__(self):
        #初始化基本的字典dict
        self.dict = {
            WordSequence.PAD_TAG: WordSequence.PAD,
            WordSequence.UNK_TAG: WordSequence.UNK,
            WordSequence.START_TAG: WordSequence.START,
            WordSequence.END_TAG: WordSequence.END,
        }
        self.fited = False #训练的标志
    #字转换成index的方法
    def to_index(self, word):
        assert self.fited, "WordSequence 尚未进行 fit 操作"
        if word in self.dict:
            return self.dict[word]
        return WordSequence.UNK
    #将index转换为字
    def to_word(self, index):
        assert self.fited, "WordSequence 尚未进行 fit 操作"
        #键值对中取数据
        for k, v in self.dict.items():
            if v == index:
                return k
        return WordSequence.UNK_TAG

    def size(self):

        assert self.fited, "WordSequence 尚未进行 fit 操作"
        return len(self.dict) + 1

    def __len__(self):
        return self.size()
    #fit函数用来训练字典。传参数（句子，最小的出现次数，最大的出现次数不限，最大的特征数不限。）
    def fit(self, sentences, min_count=5, max_count=None, max_features=None):

        assert not self.fited, 'WordSequence 只能fit一次'#判断是否被fit
        count = {} #自定义的数组
        #循环遍历
        for sentence in sentences:
            arr = list(sentence)
            #获取到的句子再进行一次循环
            for a in arr:
                #如果a未被统计，则令acount为0，若被统计则加一。
                if a not in count:
                    count[a] = 0
                count[a] += 1
        #若比最小的大，要统计，若比最大的小，也要进行统计。
        if min_count is not None:
            count = {k: v for k, v in count.items() if v >= min_count}

        if max_count is not None:
            count = {k: v for k, v in count.items() if v <= max_count}
        #字典初始化
        self.dict = {
            WordSequence.PAD_TAG: WordSequence.PAD,
            WordSequence.UNK_TAG: WordSequence.UNK,
            WordSequence.START_TAG: WordSequence.START,
            WordSequence.END_TAG: WordSequence.END,
        }
        #isinstance() 函数来判断一个对象是否是一个已知的类型，类似 type()。
        if isinstance(max_features, int):
            #对items进行一个排序
            count = sorted(list(count.items()), key=lambda x:x[1])
            if max_features is not None and len(count) > max_features:
                count = count[-int(max_features):]

            for w, _ in count:
                self.dict[w] = len(self.dict)
        else:
            #返回一个字典所有的键。
            for w in sorted(count.keys()):
                self.dict[w] = len(self.dict)
        #标记
        self.fited = True

        #拟合的过程，先将句子拿来进行统计，进行一个key value的统计

    #把句子转换成向量
    def transform(self, sentence, max_len=None):
        assert self.fited, "WordSequence 尚未进行 fit 操作"
        #进行填充操作
        if max_len is not None:
            r = [self.PAD] * max_len
        else:
            r = [self.PAD] * len(sentence)

        for index, a in enumerate(sentence):
            if max_len is not None and index >= len(r):
                break
            #存入字典
            r[index] = self.to_index(a)
        #把句子转换成向量
        return np.array(r)
#是否忽略标签类型。
    def inverse_transform(self, indices,
                          ignore_pad=False, ignore_unk=False,
                          ignore_start=False, igonre_end=False):
        ret = []
        #向量
        for i in indices:
            #向量转换为句子。
            word = self.to_word(i)
            if word == WordSequence.PAD_TAG and ignore_pad:
                continue
            if word == WordSequence.UNK_TAG and ignore_unk:
                continue
            if word == WordSequence.START_TAG and ignore_start:
                continue
            if word == WordSequence.END_TAG and igonre_end:
                continue
            ret.append(word)

        return ret

def test():

    ws = WordSequence()
    ws.fit([
        ['你', '好', '啊'],
        ['你', '好', '哦'],
    ])

    indice = ws.transform(['我', '们', '好'])
    print(indice)

    back = ws.inverse_transform(indice)
    print(back)

if __name__ == '__main__':
    test()