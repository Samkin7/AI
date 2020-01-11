from threading import Thread
from queue import Queue

class ThreadedGenerator(object):
    #初始化操作
    def __init__(self, iterator,
                 sentinel=object(), #哨兵类
                 queue_maxsize=0,   #序列
                 daemon=False):     #是否daemon
        self._iterator = iterator
        self._sentinel = sentinel
        self._queue = Queue(maxsize=queue_maxsize) #初始化队列方法。
        self._thread = Thread(
            name=repr(iterator),  #迭代器传进来
            target=self._run  #标记
        )
        self._thread.daemon = daemon
        self._started = False
        #重新定义repr，使其返回一个特定的格式。
    def __repr__(self):
        return 'ThreadedGenerator({!r})'.format(self._iterator)
    #定义run，做一个迭代。
    def _run(self):
        try:
            for value in self._iterator:
                if not self._started:
                    return
                #如果还没开始就直接return，开始后便让其加入队列中。
                self._queue.put(value)
        finally:
            self._queue.put(self._sentinel) #最后将哨兵放入


    def close(self):
        self._started = False
        try:
            while True:
                self._queue.get(timeout=30)

                #捕获键盘输入的异常。
        except KeyboardInterrupt as e:
            raise e
        except:
            pass


    def __iter__(self):
        self._started = True
        self._thread.start()
        for value in iter(self._queue.get, self._sentinel):
            yield value #做位置记录
        self._thread.join()
        self._started = False

    def __next__(self):
        if not self._started:
            self._started = True
            self._thread.start()
        value = self._queue.get(timeout=30)
        if value == self._sentinel:
            raise StopIteration()  #收集停止的迭代。
        return value

def test():

    def gene():
        i = 0
        while True:
            yield i
            i += 1

    t = gene()
    test = ThreadedGenerator(t)

    for _ in range(10):
        print(next(test))

    test.close()

if __name__ == '__main__':
    test()

