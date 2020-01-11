import re
import sys
import pickle
from tqdm import tqdm
#切分（合并句子）
def make_split(line):
    #做一个比较，若有.*等等符号，变成空格，后加入句子中
    #构造两个句子间符号的方法。
    if re.match(r'.*([，…?!\.,!？])$', ''.join(line)):
        return  []
    return [', ']
    #判断句子是否有用
def good_line(line):
    if len(re.findall(r'[a-zA-Z0-9]', ''.join(line)))>2:
        return False
    return True
#定义正则表达式的规则
def regular(sen):
    #sub实际上是替换，第一参数是规则，第二参数是替换后的句子，三参数是要处理的句子
    sen = re.sub(r'\.{3,100}', '…', sen) #出现点3到100次就将其变成三个点
    sen = re.sub(r'…{2,100}', '…', sen)
    sen = re.sub(r'[,]{1,100}', '，', sen)
    sen = re.sub(r'[\.]{1,100}', '。', sen)
    sen = re.sub(r'[\?]{1,100}', '？', sen)
    sen = re.sub(r'[!]{1,100}', '！', sen)

    return sen
#程序的处理
def main(limit=20, x_limit=3, y_limit=6):#最大长度为20，句子长度
    #创建的新的类，句子编码化处理，导入word_sequence,自己创建的类导入时要用from xx import 文件名
    from word_sequence import WordSequence

    print('extract lines') #解压文件
    #打开文件，第一参数是文件名，第二参数是读，第三参数是错误忽略，第四参数是解码类型。
    fp = open("chat_data1.conv", 'r', errors='ignore', encoding='utf-8')
    groups = []
    group = []
    #tqdm进度条，传进进度条方法，用进度条方法来显示。
    for line in tqdm(fp):
        #行开始以M开始
        if line.startswith('M '):
            #让这一行的M用空符替代。去掉M
            line = line.replace('\n', '')
            #去掉斜杠，从第二行开始就以斜杠来切分
            if '/' in line:
                line = line[2:].split('/')
            #无斜杠就直接读line
            else:
                line = list(line[2:])
            #去掉这一行最后一个字符。
            line = line[:-1]
            #得到一个group结果
            group.append(list(regular(''.join(line))))
        #以E开头的结果
        else:
            if group:
                groups.append(group)
                group = []
    if group:
        groups.append(group)
        group = []
    print('extract group')
    #解压完成。已经存入了groups中
    x_data = []
    y_data = []
    #语料对处理
    for group in tqdm(groups):
        for i, line in enumerate(group):#会有两个返回值，一个是数字，还有一个是句子。i和line进行对应。
            #定义最后一行为空
            last_line = None
            if i > 0: #代表至少有两行
                last_line = group[i - 1]#拿到最后一行
                if not good_line(last_line):#判断是否好句子。
                    last_line = None
            #设置下一行也为空
            next_line = None
            if i < len(group) - 1:
                next_line = group[i + 1]
                if not good_line(next_line):
                    next_line = None
            # 设置下下一行也为空
            next_next_line = None
            if i < len(group) -2:
                next_next_line = group[i + 2]
                if not good_line(next_next_line):
                    next_next_line = None
            #处理问答对，X和Y分别代表问答。
            if next_line:
                x_data.append(line)#把第一行设为问
                y_data.append(next_line)#最后一行设为答。
            if last_line and next_line:
                x_data.append(last_line + make_split(last_line) + line)
                y_data.append(next_line)
            if next_line and next_next_line:
                x_data.append(line)
                y_data.append(next_line + make_split(next_line) + next_next_line)

    print(len(x_data), len(y_data))
    #输出一部分问答对
    for ask, answer in zip(x_data[:20], y_data[:20]):#zip实际上python自带的命令，进行数据的整合，整合为list
        print(''.join(ask))
        print(''.join(answer))
        print('-'*20)


    data = list(zip(x_data, y_data))
    #数组类型，用{}变成字典类型，
    data = [
        (x, y)
        for x, y in data
        #limit为20，句子长度。
        if len(x) < limit \
        and len(y) < limit \
        #最短长度。
        and len(y) >= y_limit \
        and len(x) >= x_limit
    ]
    x_data, y_data = zip(*data)

    print('fit word_sequence')

    ws_input = WordSequence()
    #传进WordSequence中，词转换为向量。
    ws_input.fit(x_data + y_data)

    print('dump')
    #pickle.dump(obj, file[, protocol])序列化对象，并将结果数据流写入到文件对象中。参数protocol是序列化模式，默认值为0，表示以文本的形式序列化。protocol的值还可以是1或2，表示以二进制的形式序列化。

   #保存chatbot和ws两个文件。
    pickle.dump(
        (x_data, y_data),
        open('chatbot.pkl', 'wb')
    )
    pickle.dump(ws_input, open('ws.pkl', 'wb'))

    print('done')

if __name__ == '__main__':
    main()