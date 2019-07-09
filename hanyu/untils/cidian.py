import requests
from requests.exceptions import ConnectionError
from lxml import etree
import time



headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    # 'Accept-Language': 'en',
    'Referer': 'https://www.zdic.net/cd/bs/',
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36'
}



# 首先获取首页笔画
def get_index_page_link(url):
    time.sleep(1)
    res = requests.get(url)
    print('开始爬取：',url)
    res.encoding = 'utf-8'
    html = etree.HTML(res.text)
    cidian_index = html.xpath("//div[@class='bsul']/ul/li/a/text()")[0]
    print('该页面所有笔画为：',cidian_index)
    detail_link = 'https://www.zdic.net/cd/bs/bs/?bs={s}'
    all_links = [detail_link.format(s=i) for i in cidian_index]
    return all_links


# 获取首页笔画下的字以及深度链接
def get_index_page_under(all_links):
    print('笔画下的词语链接为：',all_links)
    for link in all_links:
        time.sleep(1)
        detail_res = requests.get(link, headers=headers)
        detail_res.encoding = 'utf-8'
        html = etree.HTML(detail_res.text)
        # wz = html.xpath("//div[@class='zlist']/li/a/text()")
        wz_links = html.xpath("//div[@class='zlist']/li/a/@href")
    return wz_links


# 请求深度链接，获取所有词语，若没有 不处理
def get_ciyu_urls(wz_links):
    print('词语链接下的所有词语为:',wz_links)
    base_url = 'https://www.zdic.net/cd/bs/{s}'
    all_urls = [base_url.format(s=i) for i in wz_links]
    # all_urls = ['https://www.zdic.net/cd/bs/ci/?z=丰']
    for url in all_urls:
        time.sleep(1)
        res = requests.get(url, headers=headers)
        # print('所有词语的页面：',res.text)

        res.encoding = 'utf-8'
        html = etree.HTML(res.text)
        try:
            if html.xpath("//div[@class='cizilist']"):
                is_page = html.xpath("//div[@class='Pages']/div[@class='Paginator']/a[@class='pck']/@href")
                if is_page:
                    all_page_nums = len(list(set(is_page)))+1
                    print('此页面有分页，共计：',all_page_nums)
                    page_urls = [url+'|'+str(page) for page in range(1,all_page_nums+1)]
                    links = []
                    for page_url in page_urls:
                        res = requests.get(page_url,headers=headers)
                        res.encoding='utf-8'
                        html = etree.HTML(res.text)
                        ciyu_links = html.xpath("//div[@class='cizilist']/li/a/@href")
                        links.extend(ciyu_links)
                    print('共计有：',len(links))
                    return links
                else:
                    print('该页面下没有分页')
                    if html.xpath("//div[@class='cizilist']/li/a/@href"):
                        # time.sleep(1)
                        # res = requests.get(url, headers=headers)
                        # res.encoding = 'utf-8'
                        # html = etree.HTML(res.text)
                        ciyu_links = html.xpath("//div[@class='cizilist']/li/a/@href")
                        print('ciyu_links:',ciyu_links)
                        return ciyu_links

        except ConnectionError:
            return None



# 页面解析函数
def parse_detail(ciyu_links):
    if ciyu_links==[]:
        print('没有数据')
        return None
    host_url = 'https://www.zdic.net'
    detail_links = [host_url+link for link in ciyu_links]
    print('词语页面解析链接:',detail_links)
    for link in detail_links:
        data = {}
        time.sleep(1)
        res = requests.get(link,headers=headers)
        res.encoding='utf-8'
        html = etree.HTML(res.text)
        # 词语名称
        data['title'] = html.xpath("//div[@class='pz']/ruby/rbc/rb/text()")[0] if html.xpath("//div[@class='pz']/ruby/rbc/rb") else ' '
        # 词语释义
        data['explain'] = html.xpath("//div[@class='gycd-item']/li/p/span[1]/text()")[0] if html.xpath("//div[@class='gycd-item']/li/p/span[1]/t") else ' '
        # 词语举例
        data['eg'] = html.xpath("//div[@class='gycd-item']/li/p/span[2]/text()")[0] if html.xpath("//div[@class='gycd-item']/li/p/span[2]") else ' '
        # 近义词
        data['synonyms'] = html.xpath("//div[@class='gycd-item']/li/p/span[3]/text()")[0] if html.xpath("//div[@class='gycd-item']/li/p/span[3]") else ' '
        print('url:',link,'data:',data)




if __name__ == '__main__':
    url = 'https://www.zdic.net/cd/bs'
    all_links = get_index_page_link(url)
    wz_links = get_index_page_under(all_links)
    ciyu_links = get_ciyu_urls(wz_links)
    parse_detail(ciyu_links)

