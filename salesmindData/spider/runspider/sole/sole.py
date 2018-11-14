import random
from threading import Thread

from utils.utils import user_agent_list
import requests
from lxml import etree
from db.base_spider import BaseSpider
from spider.models import *


class Spider(BaseSpider):
    def __init__(self, param):
        """
        初始化属性
        :param company_list: 公司列表
        """
        super(Spider, self).__init__(param=param)
        self.headers = {
            'User-Agent': random.choice(user_agent_list),
            'Referer': 'http://www.51sole.com/company/'
        }

    def parse(self, data_list):
        for data in data_list:
            company = data['data']
            url = 'http://www.51sole.com/company/searchcompany.aspx?q={}'.format(company)
            if self.sign == 0:
                detail = self.parse_list(url)
                if detail and self.sign == 0:
                    item = self.parse_detail(detail, data['data'])
                    # print(item)
                    self.col.insert(item)
                self.finish_list.append(data['id'])
            else:
                break

    def parse_list(self, url):
        while True:
            try:
                r = requests.get(url, headers=self.headers, proxies=self.get_proxy(), timeout=5)
                html = etree.HTML(r.content.decode())
                break
            except:
                continue
        nodes = html.xpath('//div[@class="about_listbox"]')
        if len(nodes) > 0:
            detail = nodes[0].xpath('//p[@class="t1_tit"]/a/@href')
            detail_url = detail[0] if len(detail) > 0 else None
        else:
            detail_url = None
        return detail_url

    def parse_detail(self, url, data):
        while True:
            try:
                r = requests.get(url, headers=self.headers, proxies=self.get_proxy(), timeout=5)
                # print(r.url)
                html = etree.HTML(r.content.decode())
                break
            except:
                continue
        item = {}
        item['输入公司名'] = data
        if 'detail' in r.url:
            company = html.xpath('//td[text()="公司名称"]/following-sibling::td/text()')
            item['公司名'] = company[0] if len(company) > 0 else ' '
            info = html.xpath('//div[@class="article"]')
            item['简介'] = info[0].xpath('string(.)').strip().replace(' ', '').replace('\r\n', '').replace('\xa0', '') if len(info) > 0 else ' '
            addr = html.xpath('//td[text()="详细地址"]/following-sibling::td/text()')
            item['地址'] = addr[0].replace(' ', '') if len(addr) > 0 else ' '
            contact = html.xpath('//i[@class="ui-icon icon-contact"]/../span/text()')
            item['联系人'] = contact[0].replace(' ', '') if len(contact) > 0 else ' '
            phone = html.xpath('//i[text()="电话："]/following-sibling::span/text()')
            item['电话'] = phone[0].replace(' ', '') if len(phone) > 0 else ' '
            telephone = html.xpath('//*[@id="imgVerify"]/@src')
            item['手机'] = telephone[0].split('phone=')[1] if len(telephone) > 0 else ' '
        else:
            company = html.xpath('//*[@id="sitewhere"]/text()')
            item['公司名'] = company[1].strip().replace('>', '').replace('\xa0', '') if len(company) > 0 else ' '
            info = html.xpath('//div[@class="profiletext"]/p/text()')
            item['简介'] = info[0].replace(' ', '').replace('\r\n', '') if len(info) > 0 else ' '
            addr = html.xpath('//i[text()="地址："]/following-sibling::span/text()')
            item['地址'] = addr[0].replace(' ', '') if len(addr) > 0 else ' '
            contact = html.xpath('//i[text()="联系人："]/following-sibling::span/text()')
            item['联系人'] = contact[0].replace(' ', '') if len(contact) > 0 else ' '
            phone = html.xpath('//i[text()="电话："]/following-sibling::span/text()')
            item['电话'] = phone[0].replace(' ', '') if len(phone) > 0 else ' '
            telephone = html.xpath('//i[text()="手机："]/following-sibling::span/text()')
            item['手机'] = telephone[0].replace(' ', '').replace('\r\n', '') if len(telephone) > 0 else ' '
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

