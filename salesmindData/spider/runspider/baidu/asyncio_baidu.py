import re
import time
from concurrent import futures
from threading import Thread

import requests
import pymongo
from lxml import html
from spider.models import *
from db.base_spider import BaseSpider


class Baidu(BaseSpider):
    def __init__(self, param):
        super(Baidu, self).__init__(param)
        self.BASE_URL = 'http://www.baidu.com/s?q1={}@V'

    def parse2(self, url):
        company_name = re.findall('q1=(.*?)@V', url)[0]
        search_result = []
        r = requests.get(url).text
        selector = html.fromstring(r)
        try:
            result = {}
            result['company_name'] = company_name
            result['search_item'] = selector.xpath(
                '//div[@class="ecl-vmp-card2"]/div[@class="ecl-vmp-contianer c-border"]/'
                'div[@class="c-row section header-section"]/h2/text()')[0]
            link = selector.xpath('//div[@class="c-row section main-section last"]/'
                                  'div[1]/table/tr[2]/td/a[1]/text()')[0]
            result['link'] = re.sub('\xa0', '', link)
            result['authentication'] = True
            result['date'] = int(time.time())
            search_result.append(result)
        except IndexError:
            for i in selector.xpath('//div[@id="content_left"]/div[position()<7]'):
                result = {}
                result['company_name'] = company_name
                result['search_item'] = ''.join(str(i).strip() for i in i.xpath('h3/a/descendant::text()'))
                link = i.xpath('div/div[@class="c-span18 c-span-last"]/div[@class="f13"]/a/descendant::text()|'
                               'div[@class="f13"]/a/text()|div/div[2]/p[2]/span[1]/text()')
                link = [''.join(str(i).strip() for i in link).replace('百度快照', '')]
                if not link:
                    link = ['']
                result['link'] = re.sub('\xa0', '', link[0])
                result['authentication'] = False
                result['date'] = int(time.time())
                search_result.append(result)
        finally:
            return search_result

    def parse(self, data_list):
        for data in data_list:
            if self.sign == 0:
                url = self.BASE_URL.format(data['data'])
                item = self.parse2(url)
                if item:
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
