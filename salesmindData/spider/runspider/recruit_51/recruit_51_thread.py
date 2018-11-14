import re
from threading import Thread

import requests
from lxml import html
from db.base_spider import BaseSpider
from spider.models import *


class Recruit_51(BaseSpider):
    def __init__(self, param):
        super(Recruit_51, self).__init__(param=param)
        self.base_url = param.get('base_url')
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.119 Safari/537.36',
        }

    def generate_url(self):
        page_num = 1
        while True:
            url = self.base_url.format(page_num)
            yield url
            page_num += 1

    def parse_url(self, url):
        while True:
            try:
                r = requests.get(url,headers=self.headers, proxies=self.get_proxy(), timeout=5).text
                selector = html.fromstring(r)
                break
            except:
                continue
        urls = [_ for _ in selector.xpath('//div[@id="resultList"]/div[@class="el"]/p/span/a/@href')]
        return urls

    def run(self):
        try:
            for url in self.generate_url():
                if self.sign == 0:
                    # print(url)
                    urls = self.parse_url(url)
                    if urls:
                        SpiderData.objects.add_data_list(data_list=urls,task_id=self.task_id)
                    elif not urls:
                        break
                else:
                    break
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


class Recruit_51_Parse(BaseSpider):
    def __init__(self, param):
        super(Recruit_51_Parse, self).__init__(param=param)
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.119 Safari/537.36',
        }

    def parse_page(self, url):
        while True:
            try:
                r = requests.get(url,headers=self.headers, timeout=5)
                r.encoding = 'gb2312'
                break
            except:
                continue
        sel = html.fromstring(r.text)
        item = {}
        for _ in sel.xpath('//div[@class="tHeader tHjob"]/div[@class="in"]/div[@class="cn"]'):
            position = _.xpath('h1/@title')
            item['position'] = ''.join(str(i) for i in position)
            location = _.xpath('span/text()')
            item['location'] = ''.join(str(i) for i in location)
            company = _.xpath('p[@class="cname"]/a/@title')
            item['company'] = ''.join(str(i) for i in company)
            industry = _.xpath('p[@class="msg ltype"]/text()')
            nature_ = ''.join(str(i).strip() for i in industry)
            try:
                item['nature'], item['scale'], item['industry'] = re.sub(r'[\r\t\xa0 ]', '', nature_).split('|')
            except Exception as e:
                item['nature'], item['scale'], item['industry'] = re.sub(r'[\r\t\xa0 ]', '', nature_).split('|'), '', ''
        for _ in sel.xpath('//div[@class="jtag inbox"]/div[@class="t1"]'):
            recruit_members_release_time = _.xpath('span[position()<5]/text()')
            for i in recruit_members_release_time:
                item['recruit_members'] = i if str(i).endswith('人') else ''
                item['release_time'] = i if str(i).endswith('发布') else ''
            item['recruit_members_release_time'] = ','.join(str(i) for i in recruit_members_release_time)
            contact = sel.xpath('//div[@class="tCompany_main"]/div[3]/descendant::text()')
            item['contact'] = re.sub(r'[\r\t\xa0\0x80\u3000 ]', '', ''.join(str(i).strip() for i in contact))
            company_info = sel.xpath('////div[@class="tCompany_main"]/div[4]/descendant::text()')
            item['company_info'] = re.sub(r'[\r\t\xa0\u3000\0x80 ]', '', ''.join(str(i).strip() for i in company_info))
            job_description = sel.xpath('//div[@class="tCompany_main"]/div[2]/descendant::text()')
            item['job_description'] = re.sub(r'[\r\t\xa0\0x80\u3000 ]', '',
                                             ''.join(str(i).strip() for i in job_description))
            item['url'] = url
        item['date'] = int(time.time())
        # print(item)
        return item

    def parse(self, data_list):
        for data in data_list:
            url = data['data']
            if self.sign == 0:
                item = self.parse_page(url)
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
