import logging
import queue
import threading

from spider_download import spider_download

global_data = threading.local()
threadLock = threading.Lock()
all_albums = set()

LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"    # 日志格式化输出
DATE_FORMAT = "%m/%d/%Y %H:%M:%S %p"                        # 日期格式
fp = logging.FileHandler('logging.txt', encoding='utf-8', mode='a')   # 日志写入文件中
fs = logging.StreamHandler()  # 日志写到控制台
logging.basicConfig(level=logging.INFO, format=LOG_FORMAT, datefmt=DATE_FORMAT, handlers=[fp, fs])


class myThread(threading.Thread):
    def __init__(self, name, q):
        threading.Thread.__init__(self)
        self.name = name
        self.q = q

    def run(self):
        logging.info("开启关键字线程：" + self.name)
        global_data.num = 0
        process_download(self.name, self.q)
        logging.info("退出关键字线程：" + self.name)


def process_download(threadName, q):
    while not workQueue.empty():
        keyword = q.get(True, 3)
        logging.info("%s processing %s" % (threadName, keyword))
        spider_download(keyword, all_albums)


def read_files():
    file_name = "46.txt"
    try:
        f = open(file_name, "r", encoding="utf-8")
        lines = f.readlines()
        print(lines)
        for line in lines:
            line = line.strip('\n')
            workQueue.put(line)
        logging.info("共添加了%d个关键词" % len(lines))
        return len(lines)
    finally:
        f.close()


workQueue = queue.Queue()
threads = []

if __name__ == "__main__":
    """
    读取文件，获取关键词，每个线程负责处理一个关键词
    """
    read_files()  # 读取文件，填充队列
    thread_num = 5  # 也可以根据read_files()返回值进行调整
    logging.info("将创建%d个线程" % thread_num)
    for num in range(1, thread_num + 1):
        thread = myThread("Thread-" + str(num), workQueue)
        threads.append(thread)  # 添加线程到线程列表
        thread.start()  # 开启线程
    # 等待所有线程完成
    for t in threads:
        t.join()
    logging.info("退出主线程")
