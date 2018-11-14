import json
import random
import time
import requests
import pymongo
from lxml import etree

from salesmindData.settings import pool
from utils.update import update_task_state
import pytesseract
from PIL import Image
from selenium import webdriver

headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'}


class WubaSpider(object):
    def __init__(self, param):
        self.company_list = param.get('company_list')
        self.BASE_URL = param.get('base_url')
        self.table_name = param.get('table_name')
        client = pymongo.MongoClient(host="139.196.29.181", port=27017)
        db = client['salesmindSpider']
        db.authenticate("spider1", "123456")
        self.collection = db[self.table_name]
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

    def parse_url(self, url):
        print(url)
        while True:
            try:
                r = requests.get(url, headers=self.headers, proxies=self.get_proxy(), timeout=3)
                html = etree.HTML(r.content.decode())
                break
            except:
                continue
        href = html.xpath('//ul[@id="list_con"]/li[1]//div[@class="comp_name"]/a/@href')
        href = href[0] if len(href) > 0 else None
        return href

    def parse_details(self, url, company):
        while True:
            try:
                r = requests.get(url, headers=self.headers, proxies=self.get_proxy(), timeout=3)
                html = etree.HTML(r.content.decode())
                break
            except:
                continue
        item = {}
        item['输入公司'] = company
        if '/mq/' in r.url:
            search_company = html.xpath('//div[@class="company_intro"]//h3/text()')
            item['爬取公司'] = search_company[0] if len(search_company) > 0 else ' '
            info = html.xpath('//p[@class="dis_non"]/text()')
            item['公司简介'] = info[0] if len(info) > 0 else ' '
            another_name = html.xpath('//div[@class="intro_down"]//tr[2]/td[1]/text()')
            item['公司别名'] = another_name[0].replace('\n', '') if len(another_name) > 0 else ' '
            scale = html.xpath('//div[@class="intro_down"]//tr[2]/td[3]/text()')
            item['规模'] = scale[0] if len(scale) > 0 else ' '
            industry = html.xpath('//div[@class="intro_down"]//tr[4]/td[1]/a/text()')
            item['行业'] = industry[0] if len(industry) > 0 else ' '
            contactor = html.xpath('//div[@class="intro_down"]//tr[4]/td[2]/text()')
            item['联系人'] = contactor[0] if len(contactor) > 0 else ' '
            phone_image = html.xpath('//div[@class="intro_down"]//tr[4]/td[3]/img/@src')
            img_url = phone_image[0] if len(phone_image) > 0 else None
            if img_url:
                r = requests.get(img_url)
                content = r.content
                file_name = r'D:\img\{}.jpg'.format(item['爬取公司'])
                with open(file_name, 'wb') as f:
                    f.write(content)
                img = Image.open(file_name)
                phone = pytesseract.image_to_string(img)
                print(phone)
                item['电话'] = phone
            else:
                item['电话'] = ' '
            addr = html.xpath('//div[@class="intro_down"]//tr[6]/td[1]/span/text()')
            item['地址'] = addr[0] if len(addr) > 0 else ' '
            print(item)
            return item
        else:
            search_company = html.xpath('//a[@class="businessName fl"]/text()')
            item['爬取公司'] = search_company[0] if len(search_company) > 0 else ' '
            info = html.xpath('//div[@class="compIntro"]/p/span[1]/text()')
            item['公司简介'] = ''.join(i.strip() for i in info) if len(info) > 0 else ' '
            scale = html.xpath('//span[text()="公司规模："]/../text()')
            item['规模'] = scale[0] if len(scale) > 0 else ' '
            industry = html.xpath('//span[text()="公司行业："]/../div/a/text()')
            item['行业'] = industry[0] if len(industry) > 0 else ' '
            contactor = html.xpath('//span[text()="联系人："]/../text()')
            item['联系人'] = contactor[0].strip() if len(contactor) > 0 else ' '
            phone_image = html.xpath('//span[text()="联系电话："]/../img/@src')
            img_url = phone_image[0] if len(phone_image) > 0 else None
            if img_url:
                r = requests.get(img_url)
                content = r.content
                file_name = r'D:\img\{}.jpg'.format(item['爬取公司'])
                with open(file_name, 'wb') as f:
                    f.write(content)
                img = Image.open(file_name)
                phone = pytesseract.image_to_string(img)
                print(phone)
                item['电话'] = phone
            else:
                item['电话'] = ' '
            addr = html.xpath('//span[text()="公司地址："]/../div/var/text()')
            item['地址'] = addr[0] if len(addr) > 0 else ' '
            print(item)
            return item

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
        for company in self.company_list:
            if self.sign == 0:
                start_url = self.BASE_URL.format(company)
                print(start_url)
                total_pn = self.parse_total_pn(start_url)
                if total_pn == 0:
                    continue
                url = self.parse_url(start_url)
                if url and self.sign == 0:
                    item = self.parse_details(url, company)
                    self.collection.insert_one(item)
                time.sleep(2)
            else:
                break
        self.update_task()

    def update_task(self):
        """from concurrent import futures

        爬虫运行完毕，更新任务状态，并退出浏览器
        :return:
        """
        update_task_state(self.table_name)
        print('58同城爬取完成')
        time.sleep(1)
