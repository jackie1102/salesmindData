from threading import Thread

import requests
import base64
from scrapy.selector import Selector
from spider.models import *
from db.base_spider import BaseSpider


class Spider(BaseSpider):
    def __init__(self, param):
        super(Spider, self).__init__(param=param)
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36',
            'Host': 'www.qymgc.com'
        }

    def parse(self, data_list):
        for data in data_list:
            data_encode = base64.b64encode(data['data'].encode()).decode()
            url = 'http://www.qymgc.com/k{}c0s0p1.html'.format(data_encode)
            while True:
                try:
                    r = requests.get(url,headers=self.headers, proxies=self.get_proxy(), timeout=5)
                    html = Selector(r)
                    break
                except Exception:
                    continue
            detail_url = html.xpath('//a[text()="进入店铺>>"]/@href').extract_first()
            if self.sign == 0:
                if detail_url and detail_url != '':
                    item = self.parse_detail(detail_url, data['data'])
                    self.col.insert(item)
                self.finish_list.append(data['id'])
            else:
                break

    def parse_detail(self, detail_url, data):
        while True:
            try:
                r = requests.get(detail_url, headers=self.headers, proxies=self.get_proxy(), timeout=5)
                html = Selector(r)
                break
            except Exception:
                continue
        item = {}
        item['输入公司名'] = data
        item['采集公司名'] = html.xpath('//h2/text()').extract_first()
        item['公司简介'] = ''.join(html.xpath('//*[@id="content"]/dd/text()').extract()).strip().replace('\n', '').replace(' ', '')
        item['联系人'] = html.xpath('//dd/p[contains(text(),"联系人：")]/text()').extract_first(default='').replace('联系人：', '')
        item['联系电话'] = html.xpath('//dd/p[contains(text(),"手机：")]/text()').extract_first(default='').replace('手机：', '')
        item['地址'] = html.xpath('//dd/p[contains(text(),"地址：")]/@title').extract_first()
        item['date'] = int(time.time())
        return item

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
