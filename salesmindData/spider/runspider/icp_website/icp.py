import urllib
import random
import copy
from threading import Thread

import requests
from lxml import etree
from db.base_spider import BaseSpider
from spider.models import *


class ICP(BaseSpider):

    def __init__(self, param):
        super(ICP, self).__init__(param=param)
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'
        }

    def parse_detail(self, url):
        while True:
            try:
                response = requests.get(url, headers=self.headers, proxies=self.get_proxy(), timeout=3)
                html = etree.HTML(response.content.decode())
                break
            except:
                continue
        query = response.url.split('value=')[1]
        query = urllib.request.unquote(query)
        item = {}
        item['name'] = query
        nodes = html.xpath('//*[@id="icp"]//tr/td[6]/a/text()')
        List = copy.copy(nodes)
        for url in List:
            try:
                try:
                    response = requests.get('http://' + url, timeout=3, verify=False)
                    # print(response.status_code)
                except:
                    response = requests.get('https://' + url, timeout=3, verify=False)
                    # print(response.status_code)
            except Exception as E:
                # print(E)
                nodes.remove(url)
        item['url'] = ';'.join(nodes)
        if item['url'] != '':
            item['date'] = int(time.time())
            self.col.insert_one(item)

    def parse(self, data_list):
        for data in data_list:
            if self.sign == 0:
                url = 'https://www.soicp.com/index.html?type=3&value=' + data['data']
                self.parse_detail(url)
                self.finish_list.append(data['id'])
                time.sleep(random.random())
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