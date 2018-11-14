from threading import Thread

from spider.models import *
from scrapy.selector import Selector
import requests
from db.base_spider import BaseSpider


class Spider(BaseSpider):
    def __init__(self, param):
        super(Spider, self).__init__(param=param)
        self.base_url = 'https://www.liepin.com/zhaopin/?sfrom=click-pc_homepage-centre_searchbox-search_new&d_sfrom=search_fp&key={}'
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36',
            'Host': 'www.liepin.com'
        }

    def parse_list(self, url):
        while True:
            try:
                r = requests.get(url, headers=self.headers, proxies=self.get_proxy(), timeout=5)
                html = Selector(r)
                break
            except Exception:
                continue
        url = html.xpath('//ul[@class="sojob-list"]/li[1]//p[@class="company-name"]/a/@href').extract_first()
        return url

    def parse_detail(self, url,data):
        while True:
            try:
                r = requests.get(url,headers=self.headers, proxies=self.get_proxy(), timeout=5, verify=False)
                html = Selector(r)
                break
            except Exception:
                continue
        item = {}
        item['输入公司名'] = data
        item['公司名'] = html.xpath('//h1/text()').extract_first()
        item['公司简介'] = html.xpath('//p[@class="profile"]/text()').extract_first(default='').strip()
        item['行业'] = html.xpath('//a[@data-selector="comp-industry"]/text()').extract_first()
        item['公司规模'] = html.xpath('//div[@class="comp-summary-tag"]/a[contains(text(),"人")]/text()').extract_first()
        item['招聘职位'] = html.xpath('//small[@data-selector="total"]/text()').extract_first()
        item['公司地址'] = html.xpath('//li[@data-selector="company-address"]/text()').extract_first()
        item['date'] = int(time.time())
        return item

    def parse(self, data_list):
        for data in data_list:
            start_url = self.base_url.format(data['data'])
            if self.sign == 0:
                detail_url = self.parse_list(start_url)
                if detail_url and detail_url != '':
                    item = self.parse_detail(detail_url, data['data'])
                    self.col.insert(item)
                self.finish_list.append(data['id'])
            else:
                break

    def run(self):
        try:
            l = self.get_data()
            cut_list = self.cut_list(l, 15)
            thread_list = []
            for data_list in cut_list:
                t = Thread(target=self.parse, args=(data_list,))
                t.start()
                thread_list.append(t)
            for t in thread_list:
                t.join()
            if self.sign == 0:
                SpiderTask.objects.finish_task2(task_id=self.task_id)
                print('{}已完成'.format(self.table_name))
            else:
                print('{}已中断'.format(self.table_name))
        except Exception as E:
            print(E)
            SpiderTask.objects.change_task2_status(task_id=self.task_id)
            print('{}已中断'.format(self.table_name))

