from threading import Thread

import requests
from scrapy.selector import Selector
from spider.models import *
from db.base_spider import BaseSpider


class Spider(BaseSpider):
    def __init__(self, param):
        super(Spider, self).__init__(param=param)
        self.base_url = param.get('base_url')
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36',
        }

    def parse_list(self):
        url = self.base_url
        while True:
            if self.sign == 0:
                while True:
                    try:
                        r = requests.get(url, headers=self.headers, proxies=self.get_proxy(), timeout=5)
                        html = Selector(r)
                        break
                    except Exception:
                        continue
                url_list = html.xpath('//ul[@class="sojob-list"]/li//h3/a/@href').extract()
                SpiderData.objects.add_data_list(data_list=url_list,task_id=self.task_id)
                next_ = html.xpath('//a[text()="下一页"]/@class').extract_first()
                if not next_ and self.sign == 0:
                    url = 'https://www.liepin.com' + html.xpath('//a[text()="下一页"]/@href').extract_first()
                else:
                    break
            else:
                break

    def run(self):
        try:
            self.parse_list()
            if self.sign == 0:
                SpiderTask.objects.finish_task1(task_id=self.task_id)
                print('{}已完成'.format(self.table_name))
            else:
                print('{}已中断'.format(self.table_name))
        except Exception as E:
            print(E)
            SpiderTask.objects.change_task1_status(task_id=self.task_id)
            print('{}已中断'.format(self.table_name))
        self.update_data_count()


class LiePinParse(BaseSpider):
    def __init__(self, param):
        super(LiePinParse, self).__init__(param=param)
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36',
        }

    def get_detail1(self, url):
        while True:
            try:
                r = requests.get(url, headers=self.headers, proxies=self.get_proxy(), timeout=5)
                html = Selector(r)
                break
            except Exception:
                continue
        item = {}
        item['职位'] = html.xpath('//h1/text()').extract_first()
        item['公司名'] = html.xpath('//h3/a/text()').extract_first()
        item['地址'] = html.xpath('//p[@class="basic-infor"]/span/a/text()').extract_first()
        item['行业'] = html.xpath('//li[contains(text(),"行业")]/a/text()').extract_first()
        item['公司规模'] = html.xpath('//li[contains(text(),"公司规模")]/text()').extract_first().replace('公司规模：', '')
        item['职位描述'] = ''.join(html.xpath('//h3[text()="职位描述："]/following-sibling::div/text()').extract()).strip()
        item['企业介绍'] = ''.join(html.xpath('//div[@class="info-word"]/text()').extract()).strip().replace('\xa0', '')
        item['date'] = int(time.time())
        return item

    def parse(self, data_list):
        for data in data_list:
            url = data['data']
            if 'http' not in url:
                url = 'https://www.liepin.com' + url
            if self.sign == 0:
                item = self.get_detail1(url)
                self.col.insert_one(item)
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