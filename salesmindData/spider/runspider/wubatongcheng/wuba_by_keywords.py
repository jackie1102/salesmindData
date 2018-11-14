import json
import random
import time
from pymongo import MongoClient
from selenium import webdriver
import requests
from lxml import etree

from salesmindData.settings import pool
from utils.update import update_task_state


class Spider(object):
    def __init__(self, param):
        self.table_name = param.get('table_name')
        client = MongoClient(host="139.196.29.181", port=27017)
        db = client['salesmindSpider']
        db.authenticate("spider1", "123456")
        self.col = db[self.table_name]
        self.driver = webdriver.Chrome()
        self.headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36',
        }
        self.sign = 0
        self.user_id = param.get('user_id')

    def get_proxy(self):
        """
        获取代理ip
        :return:
        """
        res = requests.get(
            'http://101.132.104.154:10000/get_proxy')
        content = res.content.decode()
        # print(content)
        ipdict = json.loads(content)
        ip_list = ipdict.get('ip_list')
        ip_address = random.choice(ip_list)
        proxy = {
            'http': ip_address,
            'https': ip_address,
        }
        return proxy

    def get_start_url(self):
        self.driver.get('http://sh.58.com/job/')
        while True:
            affirm = input()
            if affirm == "ok":
                start_url = self.driver.current_url
                print(start_url)
                self.driver.quit()
                return start_url

    def parse_total_pn(self, url):
        while True:
            try:
                r = requests.get(url, headers=self.headers, proxies=self.get_proxy(), timeout=3)
                html = etree.HTML(r.content.decode())
                break
            except:
                continue
        try:
            total_pn = html.xpath('//span[@class="total_page"]/text()')[0]
        except:
            total_pn = 0
        print(total_pn, '@@@')
        return int(total_pn)

    def get_total_url(self, base_url, total_pn):
        """
        获取所有页码url
        :return:
        """
        print(base_url,'@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@')
        start_url = base_url.split('?')[0] + 'pn{}/?' + base_url.split('?')[1]
        for i in range(1, int(total_pn)+1):
            yield start_url.format(i)

    def parse_list(self, url):
        while True:
            try:
                r = requests.get(url, headers=self.headers, proxies=self.get_proxy(), timeout=3)
                html = etree.HTML(r.content.decode())
                break
            except:
                continue
        nodes = html.xpath('//ul[@id="list_con"]/li')
        url_list = []
        for node in nodes:
            detail_url = node.xpath('.//div[@class="job_name clearfix"]/a/@href')[0]
            url_list.append(detail_url)
        return url_list

    def parse_detail(self, url):
        while True:
            try:
                r = requests.get(url, headers=self.headers, proxies=self.get_proxy(), timeout=3)
                html = etree.HTML(r.content.decode())
                break
            except:
                continue
        item = {}
        title = html.xpath('//span[@class="pos_title"]/text()')
        item['title'] = title[0] if len(title) > 0 else ' '
        small_title = html.xpath('//span[@class="pos_name"]/text()')
        item['small_title'] = small_title[0] if len(small_title) > 0 else ' '
        zhaopin_num = html.xpath('//div[@class="pos_base_condition"]/span[1]/text()')
        item['zhaopin_num'] = zhaopin_num[0] if len(zhaopin_num) > 0 else ' '
        addr = html.xpath('//div[@class="pos-area"]/span[2]/text()')
        item['addr'] = addr[0] if len(addr) > 0 else ' '
        company = html.xpath('//div[@class="baseInfo_link"]/a/text()')
        item['company'] = company[0] if len(company) > 0 else ' '
        industry = html.xpath('//a[@class="comp_baseInfo_link"]/text()')
        item['industry'] = industry[0] if len(industry) > 0 else ' '
        scale = html.xpath('//p[@class="comp_baseInfo_scale"]/text()')
        item['scale'] = scale[0] if len(scale) > 0 else ' '
        zhaopin_pos_num = html.xpath('//a[@class="baseInfo_link"]/text()')
        item['zhaopin_pos_num'] = zhaopin_pos_num[0] if len(zhaopin_pos_num) > 0 else ' '
        zhaopin_info = html.xpath('//div[@class="des"]/text()')
        item['zhaopin_info'] = ''.join(zhaopin_info).replace(' ', '') if len(zhaopin_info) > 0 else ' '
        company_info = html.xpath('//div[@class="shiji"]/p/text()')
        item['company_info'] = ''.join(company_info).replace(' ', '') if len(company_info) > 0 else ' '
        print(item)
        return item

    def update_task(self):
        """
        爬虫运行完毕，更新任务状态
        :return:
        """
        update_task_state(self.table_name)
        print('58前台职位爬取完成')

    def change_sign(self):
        cnn = pool.connection()
        cursor = cnn.cursor()
        while True:
            cursor.execute('select state from python_task where table_name="{}" and user_id="{}"'.format(self.table_name,self.user_id))
            state = cursor.fetchone()[0]
            if state != 1:
                self.sign = 1
                cursor.close()
                cnn.close()
                break
            time.sleep(5)

    def run(self):
        start_url = self.get_start_url()
        total_pn = self.parse_total_pn(start_url)
        if total_pn != 0 and self.sign == 0:
            for url in self.get_total_url(start_url, total_pn):
                if self.sign == 0:
                    print(url, '!!!!!!')
                    url_list = self.parse_list(url)
                    for detail_url in url_list:
                        if self.sign == 0:
                            item = self.parse_detail(detail_url)
                            self.col.insert_one(item)
                            time.sleep(2)
        if self.sign == 0:
            self.update_task()


if __name__ == '__main__':
    spider = Spider({'table_name': ''})
    spider.run()
