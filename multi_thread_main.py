import threading
import time

from spider_download import spider_main


class myThread(threading.Thread):
    def __init__(self, name, keyword):
        threading.Thread.__init__(self)
        self.name = name  # 线程名
        self.keyword = keyword  # 下载关键词

    def run(self):
        print("开启线程： " + self.name)
        # 获取锁，用于线程同步
        #      threadLock.acquire()
        spider_main(self.keyword)
        print("线程", self.name, "开始下载图片任务...")
        # 释放锁，开启下一个线程


#      threadLock.release()


def print_time(threadName, delay, counter):
    while counter:
        time.sleep(delay)
        print("%s: %s" % (threadName, time.ctime(time.time())))
        counter -= 1


def read_files():
    file_name = "46.txt"
    f = open(file_name, 'r')


if __name__ == '__main__':
    threadLock = threading.Lock()
    threads = []
    thread_num = int(input("请输入线程数："))
    # 创建新线程
    print("将创建", thread_num, "个线程")
    for num in range(1, thread_num + 1):
        thread = myThread(thread_num, "Thread-" + thread_num)
        threads.append(thread)  # 添加线程到线程列表
        thread.start()  # 开启线程

    # 等待所有线程完成
    for t in threads:
        t.join()
    print("退出主线程")
