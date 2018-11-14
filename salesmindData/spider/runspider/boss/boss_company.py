from threading import Thread

import requests
from lxml import etree
from db.base_spider import BaseSpider
from spider.models import *


class Spider(BaseSpider):

    def __init__(self, param):
        """
        初始化属性
        :param param:
        """
        super(Spider, self).__init__(param=param)
        self.base_url = 'https://www.zhipin.com/job_detail/?query={}&scity=100010000&industry=&position='
        self.headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36',
            'referer': 'https://www.zhipin.com/'
        }

    def parse_list(self, url):
        """
        解析列表页
        :param url:
        :return:
        """
        while True:
            try:
                r = requests.get(url, headers=self.headers, proxies=self.get_proxy(), timeout=3)
                html = etree.HTML(r.content.decode())
                break
            except:
                continue
        node = html.xpath('//div[@class="job-list"]//li//div[@class="company-text"]/h3/a/@href')
        detail = ['https://www.zhipin.com' + item for item in node] if len(node) > 0 else None
        return detail

    def parse_detail(self, url):
        """
        解析详情页
        :param url:
        :return:
        """
        while True:
            try:
                r = requests.get(url, headers=self.headers, proxies=self.get_proxy(), timeout=3)
                html = etree.HTML(r.content.decode())
                break
            except:
                continue
        item = {}
        company = html.xpath('//h1/text()')
        item['公司名'] = company[0] if len(company) > 0 else ' '
        node = html.xpath('//h1/../p/text()')
        item['轮次'] = node[0] if len(node) > 0 else ' '
        item['人员规模'] = node[1] if len(node) > 1 else ' '
        item['行业'] = node[2] if len(node) > 2 else ' '
        pos_num = html.xpath('//a[text()="在招职位"]/b/text()')
        item['招聘人数'] = pos_num[0] if len(pos_num) > 0 else ' '
        info = html.xpath('//div[@class="detail-content"]//div[@class="text fold-text"]/text()')
        item['简介'] = ''.join(info).replace(' ', '').replace('\xa0', '') if len(info) > 0 else ' '
        addr = html.xpath('//div[@class="location-item show-map"]/div[1]/text()')
        item['地址'] = addr[0] if len(addr) > 0 else ' '
        item['date'] = int(time.time())
        return item

    def parse(self, data_list):
        for data in data_list:
            url = self.base_url.format(data['data'])
            if self.sign == 0:
                detail_list = self.parse_list(url)
                if detail_list:
                    for detail in detail_list:
                        if self.sign == 0:
                            item = self.parse_detail(detail)
                            item['输入公司名'] = data['data']
                            self.col.insert(item)
                        else:
                            break
                    if self.sign == 0:
                        self.finish_list.append(data['id'])
            else:
                break

    def run(self):
        """
        执行过程
        :return:
        """
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
            print("{}已中断".format(self.table_name))

