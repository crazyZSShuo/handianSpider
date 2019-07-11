# -*- coding: utf-8 -*-
import scrapy
from hanyu.items import HanyuItem

class ZdicSpider(scrapy.Spider):
    name = 'zdic'
    allowed_domains = ['zdic.net']
    start_urls = ['https://www.zdic.net/cd/bs']

    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        # 'Accept-Language': 'en',
        'Referer': 'https://www.zdic.net/cd/bs/',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36'
    }

    def parse(self, response):
        cidian_index = response.xpath("//div[@class='bsul']/ul/li/a/text()").extract()
        detail_link = 'https://www.zdic.net/cd/bs/bs/?bs={s}'
        all_links = [detail_link.format(s=i) for i in cidian_index]
        for cidian_url in all_links:
            yield scrapy.Request(cidian_url,headers=self.headers,callback=self.get_index_page_under)


    def get_index_page_under(self,response):
        wz_links = response.xpath("//div[@class='zlist']/li/a/@href").extract()
        base_url = 'https://www.zdic.net/cd/bs/{s}'
        all_urls = [base_url.format(s=i) for i in wz_links]
        # print('hhhhhhhhhh:',all_urls)
        for url in all_urls:
            yield scrapy.Request(url,headers=self.headers,callback=self.get_ciyu_urls)


    def get_ciyu_urls(self,response):
        try:
            if response.xpath("//div[@class='cizilist']"):
                is_page = response.xpath("//div[@class='Pages']/div[@class='Paginator']/a[@class='pck']/@href")
                if is_page:
                    all_page_nums = len(list(set(is_page)))+1
                    print('此页面有分页，共计：',all_page_nums)
                    page_urls = [response.url+'|'+str(page) for page in range(1,all_page_nums+1)]
                    for page_url in page_urls:
                        yield scrapy.Request(page_url,headers=self.headers,callback=self.parse_detail)

                else:
                    print('该页面下没有分页')
                    # if response.xpath("//div[@class='cizilist']/li/a/@href"):
                    yield scrapy.Request(response.url,headers=self.headers,callback=self.parse_detail)


        except ConnectionError:
            return None


    def parse_detail(self,response):
        ciyu_links = response.xpath("//div[@class='cizilist']/li/a/@href").extract()
        if ciyu_links == []:
            return None
        host_url = 'https://www.zdic.net'
        detail_links = [host_url + link for link in ciyu_links]
        print('词语页面解析链接:', detail_links)
        for link in detail_links:
            yield scrapy.Request(link,headers=self.headers,callback=self.finall_parse_func)


    def finall_parse_func(self,response):
        item = HanyuItem()
        # 词语名称
        item['title'] = response.xpath("//div[@class='nr-box-header']/h2/span[1]/text()")[0].extract().strip() if response.xpath(
            "//div[@class='nr-box-header']/h2/span[1]") else ' '

        # 解释
        if response.xpath("//div[@class='jnr']/li"):# 芥蒂
            item['explain'] = response.xpath("//div[@class='jnr']/li/text()")[0].extract().strip()
        elif response.xpath("//div[@class='jnr']/p"):  # https://www.zdic.net/hans/%E4%B8%B2%E9%80%9A
            item['explain'] = ''.join(
                ''.join(response.xpath("//div[@class='jnr']/p/text()").extract()[1:]).strip().replace('∶', ',').split(
                    ',')).replace(' ', ',')
        elif response.xpath("//div[@class='jnr']"): #丰硕
            item['explain'] = response.xpath("//div[@class='jnr']/text()")[0].extract().strip()
        else:
            item['explain'] = ''

        # 词语释义
        item['chinese_mean'] = response.xpath("//div[@class='gycd-item']/li/p/span[1]/text()")[0].extract().strip()  if response.xpath(
            "//div[@class='gycd-item']/li/p/span[1]") else ' '

        # 词语举例
        item['eg'] = response.xpath("//div[@class='gycd-item']/li/p/span[2]/text()")[0].extract().strip()  if response.xpath(
            "//div[@class='gycd-item']/li/p/span[2]") else ' '

        # 近义词
        item['synonyms'] = response.xpath("//div[@class='gycd-item']/li/p/span[3]/text()")[0].extract().strip()  if response.xpath(
            "//div[@class='gycd-item']/li/p/span[3]") else ' '
        yield item



