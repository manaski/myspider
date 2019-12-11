import logging
import queue
import re
import threading
from os import mkdir, makedirs, path
import requests

global_data = threading.local()
mapLock = threading.Lock()
workQueueMap = dict()  # 相册队列字典，以关键词作为同步队列名
threads = []
all_album = set()

LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"  # 日志格式化输出
DATE_FORMAT = "%m/%d/%Y %H:%M:%S %p"  # 日期格式
fp = logging.FileHandler('logging.txt', encoding='utf-8', mode='a')  # 日志写入文件中
fp.setLevel(logging.WARNING)
fs = logging.StreamHandler()  # 日志写到控制台
logging.basicConfig(level=logging.INFO, handlers=[fp, fs])


class myThread2(threading.Thread):
    def __init__(self, name, q, keyword):
        threading.Thread.__init__(self)
        self.name = name
        self.q = q
        self.keyword = keyword

    def run(self):
        logging.info("开启下载相册线程：" + self.name)
        global_data.num = 0
        process_download(self.name, self.q, self.keyword)
        logging.info("退出下载相册线程：" + self.name)


def process_download(threadName, qmap, keyword):
    """
    从队列中取出一个相册地址，进行后续处理，每一个相册对应一个线程
    """
    if keyword not in qmap:
        # print(qmap)
        logging.error("字典为空或关键词不在字典中,线程退出%s--%s" % (threadName, keyword))
        return
    while not qmap[keyword].empty():
        album = qmap[keyword].get(True, 3)  # 从队列中取出一个相册地址，完整地址
        logging.info("%s processing album %s" % (threadName, album))
        nums = re.findall('(\d+)/', album)  # 直接从地址中匹配出相册编号
        filepath = "images/" + keyword + "/"
        if not path.exists(filepath):  # 如果目录不存在时，创建目录
            makedirs(filepath)
        record = "images/" + keyword + "/record.txt"  # 记录重复的文件夹，不再重复下载
        if nums[0] in all_album:
            fp = open(record, 'a+')  # 以二进制形式写文件
            fp.write(nums[0] + "\n")
            fp.close()
            continue
        else:
            all_album.add(nums[0])
        filepath = "images/" + keyword + "/" + nums[0] + "/"  # 拼接目录
        if not path.exists(filepath):  # 如果目录不存在时，创建目录
            makedirs(filepath)
        result = requests.get(album)
        reg = album + '\S+"'
        page_url = re.findall(reg, result.text)  # 根据正则表达式找到分页链接
        pages = set(page_url)  # 去重
        pages.add(album)  # 把第一页加进去
        # 找到页面数量最大值，进行循环，否则可能存在一些下载不到的图片
        max_num = 0
        for p in pages:
            rst = re.findall('(\d+).html', p)
            if rst:
                page_num = int(rst[0])
                max_num = max(max_num, page_num)  # 找到分页编号最大的

        global_data.i = 0  # 每个相册重新编号和计数
        global_data.failed = 0
        global_data.success = 0
        logging.info("找到了关于%s的%s号相册的%d个链接" % (keyword, nums[0], max_num))
        getimgs(album, nums[0], max_num, keyword, filepath)  # 根据每个分页链接获取图片地址
        logging.warning("下载完成: %s-%s 相册, 共下载%d张图片，其中%d张成功，%d张失败" % (keyword, str(nums[0]),
                                                                    global_data.i, global_data.success,
                                                                    global_data.failed))


def download_img(images, keyword, num, filepath):
    """
    下载每个页面上的图片,并且更改名字
    """
    logging.info('关键词:' + keyword + '的图片，现在开始下载图片...')
    for each in images:
        global_data.i += 1
        logging.info('正在下载第%d张图片，图片地址:%s' % (global_data.i, each))
        try:
            pic = requests.get(each, timeout=10)  # get请求，超时时间10s
            global_data.success += 1
        except requests.exceptions.ConnectionError:
            logging.info('【错误】当前图片无法下载,地址：%s' % each)
            global_data.failed += 1
            continue
        img_name = filepath + '/' + keyword + '_' + str(num) + '_' + str(global_data.i) + '.jpg'  # 给图片重命名
        fp = open(img_name, 'wb')  # 以二进制形式写文件
        fp.write(pic.content)
        fp.close()


def getimgs(each, num, max_num, keyword, filepath):
    """
    根据每个分页地址，最大分页数，对每个分页访问，获得所有图片地址
    """
    for page_num in range(1, max_num + 1):
        if page_num == 1:
            url = each
        else:
            url = each + str(page_num) + ".html"
        result = requests.get(url)
        reg = '"(https://ii.hywly.com/a/1/' + num + '\S+)"'
        img_url = re.findall(reg, result.text)  # 根据正则表达式找到图片地址链接
        images = set(img_url)
        logging.info("在第%d页上找到%d张图片" % (page_num, len(images)))
        download_img(images, keyword, num, filepath)


def getpages(albums, nums, keyword):
    """
    进入每个图册中后，获取分页链接，找到最多分页数目
    """
    albums = set(albums)
    nums = set(nums)
    logging.warning("关键词：%s共找到%d个相册" % (keyword, len(albums)))
    if keyword not in workQueueMap:
        workQueueMap[keyword] = queue.Queue()
    for each in albums:
        workQueueMap[keyword].put(each)  # 将相册地址加入队列中
    # print(workQueueMap)
    thread_num = min(5, len(albums))  # 线程太多会导致下载请求超时
    # 创建新线程
    for num in range(1, thread_num + 1):
        thread = myThread2(threading.currentThread().getName() + "-2-" + str(num), workQueueMap, keyword)
        threads.append(thread)  # 添加线程到线程列表
        thread.start()  # 开启线程
    # 等待所有线程完成
    for t in threads:
        t.join()
    logging.info("退出关键字线程" + threading.currentThread().getName())


def search(keyword):
    """
    输入关键词进行搜索得到一个页面并返回给下一步
    """
    url = 'https://www.meituri.com/search/' + keyword
    result = requests.get(url)
    if result:
        logging.info("关于%s的搜索成功" % keyword)
    else:
        logging.info("关于%s的搜索失败", keyword)
        raise Exception("搜索失败")
    return result


def getalbum(html, keyword):
    """
    需要根据关键词找到的第一个相册获得关键词主页
    主页相册可能包括多页，需要进行判断处理
    然后返回相册地址集合
    """
    album_url = re.findall('(https://www.meituri.com/a\S+)"', html)
    album_num = []
    if album_url:
        result = requests.get(album_url[0])
        result.encoding = "utf-8"
        # <a href="https://www.meituri.com/t/1844/" target="_blank">西野七濑</a>
        reg = 'href="(\S+)"\s+target="_blank"\>' + keyword
        home_url = re.findall(reg, result.text)  # 主页链接
        if home_url:
            homepage = requests.get(home_url[0])
            homepage.encoding = "utf-8"
            # <div class="shoulushuliang">已收录<span>3</span>套写真集，努力更新中</div>
            reg = '已收录<span>(\d+)</span>套写真集'
            all_num = re.findall(reg, homepage.text)
            logging.warning("%s的主页收录了%s个相册" % (keyword, all_num[0]))
            get_allAlbums(keyword, homepage.text, album_url, album_num)
            nextpage = "/index_1.html"
            hasnext = re.findall(nextpage, homepage.text)
            if hasnext:
                homepage = requests.get(home_url[0] + "index_1.html")
                homepage.encoding = "utf-8"
                get_allAlbums(keyword, homepage.text, album_url, album_num)
        else:
            logging.error("没有搜索到关键词为%s的主页" % keyword)
    else:
        logging.error("没有找到关键词%s相关的任何相册" % keyword)
    return album_url, album_num


def get_allAlbums(keyword, html, album_url, album_num):
    urls = re.findall('(https://www.meituri.com/a\S+)"', html)
    nums = re.findall('https://www.meituri.com/a/(\d+)/', html)
    logging.info("搜索页获得%s相册的链接：%s" % (keyword, urls))
    logging.info("搜索页获得%s相册的编号: %s" % (keyword, nums))
    album_url.extend(urls)
    album_num.extend(nums)


def spider_download(word, all_albums):
    global all_album
    all_album = all_albums
    result = search(word)  # 搜索页面
    albums, nums = getalbum(result.text, word)
    getpages(albums, nums, word)
