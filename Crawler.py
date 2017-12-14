import requests, re, time, pickle, threading, os
from lxml import etree
from datetime import date, datetime
from winsound import Beep
from jieba import analyse
from collections import defaultdict, Counter
from wordcloud import WordCloud, ImageColorGenerator
import matplotlib.pyplot as plt
from PIL import Image
import numpy as np


def crawlURLs(headers, proxy, page):
    print("Crawling page:", page, "...")
    URL = 'http://weixin.sogou.com/weixin?type=2&s_from=input&query=%E5%8C%97%E8%88%AA%E8%A1%A8%E7%99%BD%E5%A2%99&ie=utf8&_sug_=y&_sug_type_=&w=01019900&sut=267&sst0=1512997452041&lkt=1%2C1512997451940%2C1512997451940'
    URL += '&page=' + str(page)
    proxies = {}
    if proxy is not None:
        proxies = {
            'http': proxy,
            'https': proxy,
        }

    err = r'当前只显示前100条内容'

    us = []

    res = requests.get(URL, headers=headers, proxies=proxies).text
    # print(res)

    if re.search(err, res) is not None:
        print("登陆状态异常")
        return -1, []
    html = etree.HTML(res)
    atags = html.xpath(r'//ul[@class="news-list"]//h3//a')
    if len(atags) == 0:
        print('未找到内容')
        return 1, []

    for a in atags:
        title = a.xpath('string(.)')
        if re.search(r'北航表白墙', title):
            us.append(a.attrib['href'])
    print("Get", len(us), "items !")
    print("Page", page, "Finished !")
    return 0, us


def crawlList(s, e):
    urls = []
    cookie = 'IPLOC=CN1100; SUID=8929276A1620940A000000005A239A1B; SUV=1512282651056340; sct=25; SNUID=2A8A85C8A2A6C3BC1E6470D6A3A3C6A9; ld=Blllllllll2zwiotlllllVo$zuUlllllzAtIAyllll6llllljllll5@@@@@@@@@@; pgv_pvi=4611945472; LSTMV=289%2C306; LCLKINT=3209; ABTEST=0|1512989788|v1; weixinIndexVisited=1; ppinf=5|1512989870|1514199470|dHJ1c3Q6MToxfGNsaWVudGlkOjQ6MjAxN3x1bmlxbmFtZToxODolRTUlOEYlODklRTklQjglQkR8Y3J0OjEwOjE1MTI5ODk4NzB8cmVmbmljazoxODolRTUlOEYlODklRTklQjglQkR8dXNlcmlkOjQ0Om85dDJsdU93NVFmSVM0dWJXNHpkWkZlZGlrWGtAd2VpeGluLnNvaHUuY29tfA; pprdig=V_WWufz1YtpBrSw1CRT8V70Z37YjCIS2zZeKUPbb0oFdnZCnxoOepbI-kPWqHEcGuT_GHXjqGajcn0fDfdg-NfXvyKVM6j6d7qtfbvsCXMrDPL4WNvNto5oIHzJBQU-U2szT6fGJhVo8JTNaRiDY-XxdOLqtMmYP3cmA_AiC5ck; sgid=24-32409437-AVouZK4vWhiaJickjOBggegEs; SUIR=A5050B412B294B224EC1AC102C91E512; ppmdig=1513059252000000300782738520539dd456a653be9e47e0; JSESSIONID=aaanm1nFCTV6C4AaKjw8v; PHPSESSID=mi0fcp1hh5uchfdfil10bm7e93; seccodeRight=success; successCount=1|Tue, 12 Dec 2017 06:32:27 GMT'
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
        'Connection': 'keep-alive',
        'Cookie': cookie,
        'Host': 'weixin.sogou.com',
        'Referer': 'www.baidu.com',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:57.0) Gecko/20100101 Firefox/57.0',
    }

    for i in range(s, e + 1):
        err, crawl_urls = crawlURLs(headers, None, i)
        if err != 0:
            break
        urls += crawl_urls
        print("List Length :", len(urls))
        print("Set Length :", len(set(urls)))
        Beep(1200, 100)
        time.sleep(12)
    print(urls)
    f = open('URLlist-%s~%s' % (s, e), 'wb')
    pickle.dump(urls, f)
    Beep(1200, 1000)


def mergeURLlist():
    urls = []
    files = os.listdir()
    for filename in files:
        if re.search(r"URLlist", filename) is None:
            continue
        us = pickle.load(open(filename, 'rb'))
        urls += us
    pickle.dump(urls, open('URLlist', 'wb'))


def crawlProfess(url, headers, proxy):
    proxies = {}
    if proxy is not None:
        proxies = {
            'http': proxy,
            'https': proxy,
        }
    res = requests.get(url, headers=headers, proxies=proxies).text
    html = etree.HTML(res)
    posttime_str = html.xpath('//em[@id="post-date"]')[0].text
    match = re.search(r"(\d+)-(\d+)-(\d+)", posttime_str)
    if match is None:
        print("IP被限制")
        return -1, None, []

    y, m, d = match.group(1, 2, 3)
    y, m, d = int(y), int(m), int(d)
    da = date(y, m, d)
    if da < date(2017, 8, 1):
        return 1, None, []
    print("Good", da.strftime("%Y-%m-%d"))

    results = []
    spans = html.xpath('//span[@style="color: rgb(112, 48, 160); "]')
    for span in spans:
        text = span.xpath("string(.)")
        if text != '':
            results.append(text)
    return 0, da, results


def crawlPros():
    headers = {
        'Referer': 'www.baidu.com',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:57.0) Gecko/20100101 Firefox/57.0',
    }
    date2url = {}
    date2url = pickle.load(open("date2url", 'rb'))

    urls = list(date2url.values())

    date2professlist = {}

    for da, url in date2url.items():
        print(da, url)
        # err, pros = crawlProfess(urls[0], headers, None)
        # date2professlist[da] = pros
        # pickle.dump(date2professlist, open("date2professlist", 'wb'))


def date_str2date(str):
    match = re.search(r"(\d+)-(\d+)-(\d+)", str)
    y, m, d = match.group(1, 2, 3)
    y, m, d = int(y), int(m), int(d)
    da = date(y, m, d)
    return da


if __name__ == '__main__':
    headers = {
        'Referer': 'www.baidu.com',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:57.0) Gecko/20100101 Firefox/57.0',
    }
    # crawlList(71, 85)
    # mergeURLlist()
    '''
    urllist = pickle.load(open("URLlist", 'rb'))
    date2prolist = {}
    for url in urllist:
        err, da, l = crawlProfess(url, headers, None)
        Beep(1200,100)
        if err == 0:
            date2prolist[da.strftime('%Y-%m-%d')] = l[:]
            print(da.strftime('%Y-%m-%d'), l[:])
    for key, value in date2prolist.items():
        print(key, value)
    pickle.dump(date2prolist, open("date2prolist", 'wb'))
    '''
    # crawlpros
    '''
    date2professlist = pickle.load(open("date2prolist", 'rb'))
    professes = []
    s = ""
    for l in date2professlist.values():
        for pro in l:
            s += pro
            professes.append(pro)
    print('字数', len(s))
    da_max = date(2017, 1, 1)
    da_min = date(2018, 1, 1)
    for da_str in date2professlist.keys():
        da = date_str2date(da_str)
        if da > da_max:
            da_max = da
        if da < da_max:
            da_min = da
    print(da_max, da_min, da_max - da_min)
    '''

    # basic
    '''
    date2professlist = pickle.load(open("date2prolist", 'rb'))
    professes = []
    s = ""
    for l in date2professlist.values():
        for pro in l:
            s += pro
            professes.append(pro)
    kws = defaultdict(int)
    for profess in professes:
        keywords = analyse.extract_tags(profess,allowPOS=('a','ad','an','d','e'))
        # ,allowPOS=('a','ad','an','n','d','e')
        for keyword in keywords:
            kws[keyword] += 1
        print(keywords)

    kws['那个'] = kws['书院'] = 0

    mask = np.array(Image.open(r'img/rose.jpg'))
    image_colors = ImageColorGenerator(mask)
    wc = WordCloud(background_color='white',
                   font_path=r'C:\Windows\Fonts\simhei.ttf',
                   mask=mask, ).generate_from_frequencies(kws)
    plt.figure()
    plt.imshow(wc.recolor(color_func=image_colors), interpolation="bilinear")
    # plt.imshow(wc)
    plt.axis("off")
    plt.show()
    '''
    # wordcloud
    '''
    date2professlist = pickle.load(open("date2prolist", 'rb'))
    professes = []
    s = ""
    for l in date2professlist.values():
        for pro in l:
            s += pro
            professes.append(pro)

    d = [0 for i in range(7)]
    d1 = ot = d2 = d3 = d4 = 0

    for profess in professes:
        profess = profess[6:]
        # 士谔书院、冯如书院、士嘉书院、守锷书院、致真书院、知行书院
        if re.search(r"大一", profess) is not None \
                or re.search(r"17", profess) is not None \
                or re.search(r"士谔", profess) is not None \
                or re.search(r"冯如", profess) is not None \
                or re.search(r"士嘉", profess) is not None \
                or re.search(r"守锷", profess) is not None \
                or re.search(r"致真", profess) is not None \
                or re.search(r"知行", profess) is not None:
            d1 += 1
        if re.search(r"大二", profess) is not None or re.search(r"16", profess) is not None:
            ot += 1
            d2 += 1
        if re.search(r"大三", profess) is not None or re.search(r"15", profess) is not None:
            ot += 1
            d3 += 1
        if re.search(r"大四", profess) is not None or re.search(r"14", profess) is not None:
            ot += 1
            d4 += 1
        if re.search(r"学长", profess) is not None or re.search(r"学姐", profess) is not None:
            ot += 1

        if re.search(r"士谔", profess) is not None:
            d[1] += 1
        if re.search(r"冯如", profess) is not None:
            d[2] += 1
        if re.search(r"士嘉", profess) is not None:
            d[3] += 1
        if re.search(r"守锷", profess) is not None:
            d[4] += 1
        if re.search(r"致真", profess) is not None:
            d[5] += 1
        if re.search(r"知行", profess) is not None:
            d[6] += 1
    print(d)
    print(d1, d2, d3, d4, ot)
    print(len(professes))
    '''
    # vs & pk
    date2professlist = pickle.load(open("date2prolist", 'rb'))
    professes = []
    s = ""
    for l in date2professlist.values():
        for pro in l:
            s += pro
            professes.append(pro)
    d1, ot = 0, 0
    d = [0 for i in range(7)]

    kws = defaultdict(int)

    print(len(professes))
    print(len(set(professes)))

    for profess in professes:
        profess = profess[6:]
        keywords = analyse.extract_tags(profess, allowPOS=('n',))
        # ,allowPOS=('a','ad','an','n','d','e')
        for keyword in keywords:
            kws[keyword] += 1
            # print(keywords)
    counter = Counter(kws)
    for key, value in counter.most_common(100):
        print(key, value)
    for key, value in counter.most_common(100):
        print(key)
    for key, value in counter.most_common(100):
        print(value)

    # print(len(counter.most_common(100)))
