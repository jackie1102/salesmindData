from threading import Thread

import requests
from lxml import etree
from db.base_spider import BaseSpider
from spider.models import *


class Spider(BaseSpider):
    def __init__(self, param):
        super(Spider, self).__init__(param=param)
        self.base_url = param.get('base_url') + '&page={}'
        self.page_totle = int(param.get('page_totle'))

    def run(self):
        url_list = []
        for i in range(1, self.page_totle + 1):
            url_list.append(self.base_url.format(i))
        SpiderData.objects.add_data_list(data_list=url_list, task_id=self.task_id)
        task = SpiderTask.objects.get_one_task(id=self.task_id)
        task.data_totle = len(url_list) + task.data_totle
        task.save()
        SpiderTask.objects.finish_task1(task_id=self.task_id)


class SpiderParse(BaseSpider):

    def __init__(self, param):
        """
        初始化属性
        :param param:
        """
        super(SpiderParse, self).__init__(param=param)
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
        node_list = html.xpath('//div[@class="job-list"]//li')
        if len(node_list) > 0:
            item_list = []
            for node in node_list:
                item = {}
                title = node.xpath('.//div[@class="job-title"]/text()')
                item['职位标题'] = title[0] if len(title) > 0 else ' '
                company = node.xpath('.//div[@class="company-text"]/h3/a/text()')
                item['公司名'] = company[0] if len(company) > 0 else ' '
                addr = node.xpath('.//div[@class="info-primary"]/h3[@class="name"]/following-sibling::p/text()')
                item['地址'] = addr[0] if len(addr) > 0 else ' '
                p = node.xpath('.//div[@class="info-company"]//h3[@class="name"]/following-sibling::p/text()')
                item['行业'] = p[0] if len(p) > 0 else ' '
                item['轮次'] = p[1] if len(p) > 1 else ' '
                item['规模'] = p[2].replace('人', '') if len(p) > 2 else ' '
                date = node.xpath('.//p[contains(text(), "发布")]/text()')
                item['发布日期'] = date[0] if len(date) > 0 else ' '
                item['date'] = int(time.time())
                item_list.append(item)
            if len(item_list) > 0:
                self.col.insert(item_list)

    def parse(self, data_list):
        for data in data_list:
            list_url = data['data']
            if self.sign == 0:
                self.parse_list(list_url)
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
            print('{}已中断'.format(self.table_name))

