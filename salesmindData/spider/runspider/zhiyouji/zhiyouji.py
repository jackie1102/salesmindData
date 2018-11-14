import time
from threading import Thread

from lxml import etree
import requests
from db.base_spider import BaseSpider
from spider.models import *


class Spider(BaseSpider):
    def __init__(self, param):
        super(Spider, self).__init__(param=param)
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'
        }

    def parse(self, data_list):
        for data in data_list:
            company = data['data']
            url = 'http://www.jobui.com/cmp?keyword={}&area=%E5%85%A8%E5%9B%BD'.format(company)
            if self.sign == 0:
                detail_url = self.parse_list(url)
                if detail_url:
                    item = self.parse_detail(detail_url)
                    item['输入公司名'] = company
                    self.col.insert_one(item)
                self.finish_list.append(data['id'])
            else:
                break

    def parse_list(self, url):
        """
        解析列表页，抓取列表第一个详情url
        :param url:
        :return:
        """
        while True:
            try:
                r = requests.get(url, headers=self.headers, proxies=self.get_proxy(), timeout=5)
                break
            except requests.RequestException:
                continue
        html = etree.HTML(r.content.decode())
        node = html.xpath('//ul[@class="companyList"]/li[1]//h2//a/@href')
        detail_url = 'http://www.jobui.com' + node[0] if len(node) > 0 else None
        return detail_url

    def parse_detail(self, url):
        """
        解析详情页
        :param url:
        :return:
        """
        while True:
            try:
                r = requests.get(url, headers=self.headers,proxies=self.get_proxy(), timeout=5)
                break
            except requests.RequestException:
                continue
        html = etree.HTML(r.content.decode())
        item = {}
        company = html.xpath('//*[@id="companyH1"]/a/text()')
        item['公司名'] = company[0] if len(company) > 0 else ' '
        com_info = html.xpath('//dt[text()="公司信息："]/following-sibling::dd[1]/text()')
        item['公司信息'] = com_info[0] if len(com_info) > 0 else ' '
        industry = html.xpath('//dt[text()="公司行业："]/following-sibling::dd[1]/a/text()')
        item['公司行业'] = ''.join(industry) if len(industry) > 0 else ' '
        small_name = html.xpath('//dt[text()="公司简称："]/following-sibling::dd[1]/text()')
        item['公司简称'] = small_name[0] if len(small_name) > 0 else ' '
        info = html.xpath('//*[@id="textShowMore"]/text()')
        item['公司简介'] = ''.join(info) if len(info) > 0 else ' '
        num = html.xpath('//a[text()="招聘"]/span/text()')
        item['招聘数量'] = num[0].replace(' ', '') if len(num) > 0 else '-'
        addr = html.xpath('//dt[text()="公司地址："]/following-sibling::dd[1]/text()')
        item['公司地址'] = addr[0] if len(addr) > 0 else '-'
        web = html.xpath('//dt[text()="公司网站："]/following-sibling::dd[1]/a/text()')
        item['官方网站'] = web[0] if len(web) > 0 else '-'
        contact = html.xpath('//div[@class="j-shower1 dn"]/dd/text()')
        item['联系方式'] = contact[0] if len(contact) > 0 else '-'
        item['date'] = int(time.time())
        # print(item)
        return item

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
