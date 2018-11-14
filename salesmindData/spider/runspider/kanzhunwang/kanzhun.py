from threading import Thread

from lxml import etree
import requests
from spider.models import *
from db.base_spider import BaseSpider


class Spider(BaseSpider):
    def __init__(self, param):
        super(Spider, self).__init__(param=param)
        self.base_url = param.get('base_url')
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36'
        }

    def parse_list(self, url):
        """
        解析列表页
        :param url:
        :return:
        """
        url_list = []
        while True:
            try:
                r = requests.get(url, headers=self.headers, proxies=self.get_proxy(), timeout=3)
                break
            except:
                continue
        html = etree.HTML(r.content.decode())
        node_list = html.xpath('//a[@class="img"]/@href')
        print(node_list)
        num = len(node_list)
        if num >= 5:
            num = 5
        for node in node_list[:num]:
            url = 'https://www.kanzhun.com' + node
            url_list.append(url)
        return url_list

    def parse_detail(self, url):
        """
        解析详情页
        :param url:
        :return:
        """
        while True:
            try:
                r = requests.get(url, headers=self.headers, proxies=self.get_proxy(), timeout=3)
                break
            except:
                continue
        html = etree.HTML(r.content.decode())
        item = {}
        company = html.xpath('//strong/text()')
        item['company'] = company[0] if len(company) > 0 else ' '
        industry = html.xpath('//div[@class="industry"]/span/text()')
        item['industry'] = industry[0] if len(industry) > 0 else ' '
        person = html.xpath('//div[@class="person"]/span/text()')
        item['person'] = person[0] if len(person) > 0 else ' '
        city = html.xpath('//div[@class="city"]/span/text()')
        item['city'] = city[0] if len(city) > 0 else ' '
        info = html.xpath('//div[@class="co_desc"]/text()')
        item['info'] = info[0].replace('\n', '').replace(' ', '') if len(info) > 0 else ' '
        return item

    def parse(self, data_list):
        for data in data_list:
            url = self.base_url.format(data['data'])
            if self.sign == 0:
                url_list = self.parse_list(url)
                for detail in url_list:
                    if self.sign == 0:
                        item = self.parse_detail(detail)
                        item['输入公司名'] = data['data']
                        item['date'] = int(time.time())
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
                print("{}已中断".format(self.table_name))
        except Exception as E:
            print(E)
            SpiderTask.objects.change_task2_status(task_id=self.task_id)
            print('{}已中断'.format(self.table_name))

