import json
import threading
import time
import urllib

from spider.models import save_task
from spider.runspider.zdao.conf import *
from salesmindData.settings import pool
import requests
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from spider.runspider.zdao.base_spider_zaodao import BASEZAODAO
from lxml import etree


class ZAODAOSPEO(BASEZAODAO):

    def __init__(self, data_str, table_name, username, password, start_page):
        """
        初始化属性
        :param area_list: list 地区列表
        :param keywords: str 关键词
        :param table_name: str 表名
        :param cookies: list COOKIE值
        """
        super(ZAODAOSPEO, self).__init__(table_name=table_name, username=username, password=password)
        self.data_str = data_str
        self.username = username
        self.password = password
        self.table_name = table_name
        self.start_page = start_page
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36',
            'Host': 'www.zdao.com',
            'X-Requested-With': 'XMLHttpRequest',
            'Origin': 'https://www.zdao.com',
            'Cookie': ''
        }

    def parse_data(self):
        data_str = urllib.parse.unquote(self.data_str)
        data_list = data_str.split('&')
        list1 = []
        list2 = []
        for i in data_list:
            list1.append(i.split('=')[0])
            list2.append(i.split('=')[1])
        data = dict(zip(list1, list2))
        return data

    def get_headers(self):
        '''
        将从浏览器上Copy来的cookie字符串转化为Scrapy能使用的Dict
        :return:
        '''
        cookie = [item["name"] + "=" + item["value"] for item in self.driver.get_cookies()]
        cookiestr = ';'.join(item for item in cookie)
        self.headers['Cookie'] = cookiestr
        self.driver.quit()

    def save_url(self, url):
        """
        储存url
        :param detail_url:
        :return:
        """
        cnn = pool.connection()
        cursor = cnn.cursor()
        task = cursor.execute(
            'select * from zdao_spider_url WHERE table_name ="{}" AND user_id="{}" and detail_url="{}";'.format(
                TABLE_NAME, USER_ID, url))
        if not task:
            cursor.execute(
                'insert into zdao_spider_url (detail_url,table_name,user_id,start_time) '
                'values ("{}","{}","{}",NOW());'.format(url, TABLE_NAME, USER_ID))
        cursor.close()
        cnn.close()

    def get_list(self):
        data = self.parse_data()
        i = self.start_page
        while True:
            data['start'] = i * 20
            print(data)
            while True:
                try:
                    r = requests.post('https://www.zdao.com/info/searchPerson', data=data, headers=self.headers,
                                      timeout=5)
                    break
                except Exception as E:
                    print(E)
                    continue
            data1 = json.loads(r.content.decode())
            if data1['errno'] != 0:
                print(data1)
                self.driver = webdriver.Chrome()
                self.wait = WebDriverWait(self.driver, 5)
                self.driver.get('https://www.zdao.com/user/login')
                time.sleep(2)
                try:
                    self.login()
                    self.get_headers()
                except:
                    pass
                self.driver.quit()
                continue
            if data1['data']['num'] != 0:
                for item in data1['data']['items']:
                    url = 'https://www.zdao.com/account/main?id={}&utype=0'.format(item['cp_id'])
                    self.save_url(url)
                if i < 50:
                    i += 1
                    time.sleep(5)
                else:
                    break
            else:
                break


    def run(self):
        """
        获取列表页、解析列表，详情页、完成退出
        :return:
        """
        self.login()
        self.get_headers()
        self.get_list()
        print('{}url抓取完成'.format(TABLE_NAME))


def run_zdao():
    spider = ZAODAOSPEO(data_str=data_str, table_name=TABLE_NAME, username=username,
                        password=password, start_page=start_page)
    spider.run()


if __name__ == '__main__':
    T = threading.Thread(target=run_zdao)
    T.start()
    thread_id = T.ident
    save_task(TABLE_NAME, USER_ID)
