import requests
import re
import urllib
from bs4 import BeautifulSoup


def get_html_text(url):
    '''
    获取网址url的HTML代码，以字符串形式返回html代码

    '''
    try:
        res = requests.get(url, timeout=6)
        res.raise_for_status()
        res.encoding = res.apparent_encoding
        return res.text
    except:
        return ''
        print('请求异常')


def get_grupic_url(page_url, grupic_url_list, key_url, key_word):
    '''
    获取每张页面中每个图册的url链接，每个图册的url都有共同
    且有别于其他链接的url，我们把部分特征的字符串放在key_url
    中，通过它我们就可以筛选出页面中所有图册的url

    '''
    page_html = get_html_text(page_url)
    # 解析页面的html代码
    soup = BeautifulSoup(page_html, 'html.parser')
    # 获取该页面html代码中的所有<a>标签
    a_tags = soup.find_all('a', attrs={'href': True})

    select_atag(grupic_url_list, a_tags, key_url, key_word)


def get_allpages_url(cover_url, pages_url_list):
    '''通过递归获取所有页面的链接，
        直到该页面不存在class = 'next'的<a>标签

    '''
    html = get_html_text(cover_url)
    soup = BeautifulSoup(html, 'html.parser')
    # 找到属性class = 'next'的<a>标签
    a_tags = soup.find_all('a', class_='next')
    # 如果<a>标签存在，就将该标签的url加入列表
    if a_tags:
        nextpage_url = a_tags[0].get('href')
        pages_url_list.append(nextpage_url)
        # 递归获取下一个页面的<a>标签
        get_allpages_url(nextpage_url, pages_url_list)
    # 当不存在属性class = 'next'的<a>标签时，说明这是最后一页，结束递归
    return None


def download_each_page(grupic_url_list, file_path1, page):
    '''
    通过调用download_each_group()函数，
    下载每一页中的所有组图

    '''
    print('\n\n第 {0} 页开始下载：\n'.format(str(page)))

    gup = 1  # 组数标记
    # 下载该页面中每个小相册的所有图片
    for grupic_url in grupic_url_list:
        file_path2 = file_path1 + '_{0}'.format(str(gup))
        # 获取该页面的h1标题
        h1_string = get_h1_string(grupic_url)
        try:
            download_each_group(grupic_url, file_path2, h1_string, gup)
            gup += 1
        except:
            print("下载异常")
            gup += 1
            continue


def download_all_page(pages_url_list, file_path, key_url, key_word):
    '''通过调用函数download_each_page()，
        来下载所有页面的图片

    '''
    pages_num = len(pages_url_list)
    print('\n相册一共有 {0} 页，已经开始下载请您耐心等待...'.format(str(pages_num)))

    page = 1  # 页数标记
    for page_url in pages_url_list:
        grupic_url_list = []
        get_grupic_url(page_url, grupic_url_list, key_url, key_word)
        file_path1 = file_path + r'\{0}'.format(str(page))
        download_each_page(grupic_url_list, file_path1, page)
        page += 1


def download_each_group(grupic_url, file_path, h1_string, gup, n=1):
    '''
    进入链接为grupic_url的图册，下载我们需要的大图片，
    并递归进入下一个页面开始下载，直到图册的h1标题发生改变

    '''
    new_file_path = file_path + '_{0}.jpg'.format(str(n))
    n += 1
    html = get_html_text(grupic_url)
    soup = BeautifulSoup(html, 'html.parser')
    # 当该页面的h1标题和小相册封面的h1标题相同时开始下载
    if h1_string == soup.h1.string:
        # 找到属性class_ = 'pic-large'的img标签
        img_tags = soup.find_all('img', class_='pic-large')
        img_tag = img_tags[0]
        # 下载该img标签属性data-original提供的url链接，即为目标图片的链接
        urllib.request.urlretrieve(img_tag.get('data-original'), new_file_path)
        # 获取下一个页面的链接
        next_url = img_tag.parent.get('href')
        print('第 {0} 组：{1}, 第 {2} 张下载完成啦'.format(str(gup), h1_string, str(n - 1)))
        # 递归下载下一个页面的目标图片
        download_each_group(next_url, file_path, h1_string, gup, n)
    # 当h1标题不同时，说明进入到了另一个小相册，结束递归
    return None


def get_h1_string(url):
    '''
    获取网址为url网站的h1标签内容

    '''
    try:
        html = get_html_text(url)
        soup = BeautifulSoup(html, 'html.parser')
        return soup.h1.string
    except:
        print('h1标题获取异常')
        return ''


def select_atag(grupic_url_list, atags, key_url, key_word):
    for atag in atags:
        atag_string = str(atag)
        soup = BeautifulSoup(atag_string, 'html.parser')
        p = soup.p
        url = atag.get('href')
        if soup.img and p and re.search(key_word, p.string) and re.match(key_url, url):
            grupic_url_list.append(atag.get('href'))


def main():
    '''
    主函数

    '''
    # 封面的url链接，也就是第一页的url链接 http://www.win4000.com/wallpaper_detail_163954.html
    cover_url = 'http://www.win4000.com/mt/yangzi.html'
    # 小相册链接中有别于其他链接的特征字符串
    key_url = r'http://www.win4000.com/meinv'
    key_word = '杨紫'
    # 图片存放的目录
    file_path = r'images\yangzi'

    # 存放所有页面链接的列表
    pages_url_list = []
    # 先将封面，即第一页加入列表
    pages_url_list.append(cover_url)

    # 获取其他页面的链接
    get_allpages_url(cover_url, pages_url_list)

    # 下载所有页面中所有图片的函数
    download_all_page(pages_url_list, file_path, key_url, key_word)


main()
