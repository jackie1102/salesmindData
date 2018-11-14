import json
import random
import time
import urllib
import requests
from lxml import etree
from selenium import webdriver
from spider.runspider.zdao.base_spider_zaodao import BASEZAODAO
from selenium.webdriver.support.ui import WebDriverWait
import logging
from utils.update import update_task_state
logger = logging.getLogger('django')


class ZAODAOSPEO(BASEZAODAO):

    def __init__(self, data_str, table_name, username, password):
        """
        初始化属性
        :param area_list: list 地区列表
        :param keywords: str 关键词
        :param table_name: str 表名
        :param cookies: list COOKIE值
        """
        super(ZAODAOSPEO, self).__init__(table_name=table_name, username=username, password=password)
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36',
            'Host': 'www.zdao.com',
            'X-Requested-With': 'XMLHttpRequest',
            'Origin': 'https://www.zdao.com',
        }
        self.data_str = data_str

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

    def get_list(self):
        url_list = set()
        data = self.parse_data()
        for i in range(3):
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
                try:
                    if data1['errno'] != 0:
                        print(data)
                        self.driver = webdriver.Chrome()
                        self.wait = WebDriverWait(self.driver, 5)
                        self.driver.get('https://www.zdao.com/user/login')
                        time.sleep(2)
                        try:
                            self.check_YZM()
                        except:
                            pass
                        self.driver.quit()
                    for item in data1['data']['items']:
                        url = 'https://www.zdao.com/account/main?id={}&utype=0'.format(item['cp_id'])
                        url_list.add(url)
                    break
                except Exception as E:
                    print(E)
                    continue
            time.sleep(5)
        print(url_list)
        return url_list

    def get_detail(self, url):
        """
        解析详情页
        :return: dic  item:采集数据
        """
        while True:
            while True:
                try:
                    r = requests.get(url, headers=self.headers, timeout=5)
                    content = r.content.decode()
                    break
                except:
                    continue
            try:
                code = json.loads(content)['errno']
                if code != 0:
                    self.driver = webdriver.Chrome()
                    self.wait = WebDriverWait(self.driver, 5)
                    self.driver.get('https://www.zdao.com/user/login')
                    import time
                    time.sleep(2)
                    try:
                        self.check_YZM()
                    except:
                        pass
                    self.driver.quit()
            except:
                break
        html = etree.HTML(r.content.decode())
        item = {}
        name = html.xpath('//p[@class="user_name"]/text()')
        item['姓名'] = name[0] if len(name) > 0 else ' '
        position = html.xpath('//p[@class="user_title"]/text()')
        item['职位'] = position[0] if len(position) > 0 else ' '
        company = html.xpath('//div[@class="user_career"]/a/text()')
        item['公司'] = company[0] if len(company) > 0 else ' '
        slogan = html.xpath('//p[@class="business"]/text()')
        item['slogan'] = slogan[0].strip() if len(slogan) > 0 else ' '
        company_name = html.xpath(
            '//div[@class="content_main company_container"]//div[@class="small_title"]/text()')
        item['公司名'] = company_name[0].strip() if len(company_name) > 0 else ' '
        time = html.xpath('//div[@class="content_main company_container"]//div[@class="half_item_info"][1]/text()')
        item['成立时间'] = time[0].split('：')[1].replace('注册资本', '').strip() if len(time) > 0 else ' '
        try:
            item['注册资本'] = \
            html.xpath('//div[@class="content_main company_container"]//div[@class="half_item_info"][1]/text()')[
                0].split('：')[-1].strip()
        except:
            item['注册资本'] = ' '
        try:
            try:
                school = html.xpath(
                    '//div[@class="content_main ib experience"]/div[2]//div[@class="name"]/text()')[0]
            except:
                school = ''
            try:
                major = html.xpath(
                    '//div[@class="content_main ib experience"]/div[2]//div[@class="half_item_info major"]/text()')[
                    0]
            except:
                major = ''
            try:
                time = html.xpath(
                    '//div[@class="content_main ib experience"]/div[2]//div[@class="half_item_info education_time"]/text()')[
                    0]
            except:
                time = ''

            item['教育经历'] = school + '>' + major + '>' + time
        except:
            item['教育经历'] = ' '
        try:
            item['邮箱'] = html.xpath('//a[contains(@class,"mail_item")]/text()')[0].strip()
        except:
            item['邮箱'] = ' '
        try:
            item['QQ'] = html.xpath('//div[contains(@class,"QQ_item")]/text()')[0].strip()
        except:
            item['QQ'] = ' '
        try:
            item['微信'] = html.xpath('//div[contains(@class,"weixin_item")]/text()')[0].strip()
        except:
            item['微信'] = ' '
        try:
            item['手机'] = html.xpath('//a[contains(@class,"mobile_item")]/text()')[0].strip()
        except:
            item['手机'] = ' '
        try:
            item['性别'] = html.xpath('//div[contains(@class,"gender")]/text()')[0]
        except:
            item['性别'] = ' '
        try:
            item['所属行业'] = html.xpath('//div[contains(@class,"industry_name")]/text()')[0]
        except:
            item['所属行业'] = ' '
        try:
            item['所在地区'] = html.xpath('//div[@class="item_info town_code"]/text()')[0]
        except:
            item['所在地区'] = ' '
        try:
            item['家乡'] = html.xpath('//div[@class="item_info hometown_code"]/text()')[0]
        except:
            item['家乡'] = ' '
        print(item)
        return item

    def run(self):
        """
        获取列表页、解析列表，详情页、完成退出
        :return:
        """
        self.login()
        self.get_headers()
        url_list = list(self.get_list())
        for url in url_list:
            item = self.get_detail(url)
            self.col.insert(item)
            time.sleep(3)
        self.update_task()


class ZAODAOSCOM(BASEZAODAO):

    def __init__(self, company_list, table_name, cookies, area=None):
        """
        初始化属性
        :param company_list: 公司列表
        :param table_name: 数据库表名
        :param cookies:
        :param area: 地区
        """
        super(ZAODAOSCOM, self).__init__(table_name=table_name, cookies=cookies)
        self.company_list = company_list
        self.area = area

    def get_list(self):
        """
        在浏览器中添加COOKIES 并进行搜索
        :return:
        """
        self.driver.get('https://www.zdao.com/user/login')
        # 在浏览器中添加cookie
        for cookie in self.cookies:
            self.driver.add_cookie(cookie)
        time.sleep(1)
        for company in self.company_list:
            self.driver.get('https://www.zdao.com/site/search')
            time.sleep(2)
            try:
                self.driver.find_element_by_xpath('/html/body/div[5]/div[2]/i').click()
            except Exception as E:
                logger.error(E)
            current_url = self.driver.current_url
            if 'captcha' in current_url:
                self.driver.refresh()
            try:
                self.check_YZM()
                time.sleep(3)
            except Exception as E:
                print(E)
                logger.error(E)
            # 输入关键词
            self.driver.find_element_by_xpath('//input[@class="search_input"]').send_keys(company)
            time.sleep(1)
            # 点击搜索
            self.driver.find_element_by_id('btn_search').click()
            time.sleep(2)
            if self.area != None and self.area != '':
                area_list = self.area.spilt('/')
                self.driver.find_element_by_id('filter_btn_area').click()
                if len(area_list) == 2:
                    self.driver.find_element_by_xpath('//div[@data-name="{}"]/span'.format(area_list[0])).click()
                    self.driver.find_element_by_xpath('//div[@data-name="{}"]/span'.format(area_list[1])).click()
                else:
                    self.driver.find_element_by_xpath('//div[@data-name="{}"]/span'.format(area_list[0])).click()
                time.sleep(2)
            self.parse_list()

    def parse_list(self):
        """
        在新窗口打开详情页
        获取并保存数据
        :return:
        """
        url = self.driver.find_element_by_xpath('//div[@class="company_list"]/a[1]').get_attribute('href')
        js = 'window.open("{}");'.format(url)
        self.driver.execute_script(js)
        handles = self.driver.window_handles
        for handle in handles:  # 切换窗口
            if handle != self.driver.current_window_handle:
                self.driver.switch_to.window(handle)
        value = self.get_detail()
        self.col.insert_one(value)
        self.driver.close()
        self.driver.switch_to.window(handles[0])

    def get_detail(self):
        """
        解析详情页
        :return:
        """
        item = {}
        return item

    def run(self):
        """
        执行过程
        :return:
        """
        self.get_list()
        self.parse_list()
        update_task_state(self.table_name)
        self.driver.quit()
        print('爬去完成')


class ZAODAOSPRO(BASEZAODAO):

    def __init__(self, area_list, keywords, table_name, cookies):
        """
        初始化属性
        :param area_list:  list 地区列表
        :param keywords: str 关键词
        :param table_name: str 数据库表名
        :param cookies:
        """
        super(ZAODAOSPRO, self).__init__(table_name=table_name, cookies=cookies)
        self.area_list = area_list
        self.keywords = keywords

    def get_list(self):
        """
        在浏览器中添加COOKIES 并进行搜索
        :return:
        """
        self.driver.get('https://www.zdao.com/user/login')
        # 在浏览器中添加cookie
        for cookie in self.cookies:
            self.driver.add_cookie(cookie)
        time.sleep(1)
        self.driver.get('https://www.zdao.com/site/searchproduct')
        time.sleep(2)
        self.driver.find_element_by_xpath('/html/body/div[5]/div[2]/i').click()
        current_url = self.driver.current_url
        if 'captcha' in current_url:
            self.driver.refresh()
        try:
            self.check_YZM()
            time.sleep(3)
        except Exception as E:
            print(E)
            logger.error(E)
        # 输入关键词
        self.driver.find_element_by_xpath('//input[@class="search_input"]').send_keys(self.keywords)
        time.sleep(1)
        # 点击搜索
        self.driver.find_element_by_id('btn_search').click()
        time.sleep(2)

    def parse_list(self):
        """
        对列表页进行解析，抓取详情页，并持久化数据
        :return:
        """
        while True:
            try:
                try:
                    current_url = self.driver.current_url
                    if 'captcha' in current_url:
                        self.driver.refresh()
                        time.sleep(2)
                    self.check_YZM()
                    time.sleep(2)
                except:
                    pass
                current_url = self.driver.current_url
                print(current_url)
                for area in self.area_list:
                    area_0 = area[0]
                    area_1 = area[1]
                    # 选择地区
                    self.driver.find_element_by_id('filter_btn_area').click()
                    self.driver.find_element_by_xpath('//div[@data-name="{}"]/span'.format(area_0)).click()
                    if area_1 != '':
                        self.driver.find_element_by_xpath('//div[@data-name="{}"]/span'.format(area_1)).click()
                    time.sleep(2)
                    url_list = []
                    while True:
                        try:
                            # 检测验证码
                            self.check_YZM()
                            time.sleep(2)
                            # 选择地区
                            self.driver.find_element_by_id('filter_btn_area').click()
                            self.driver.find_element_by_xpath('//div[@data-name="{}"]/span'.format(area_0)).click()
                            if area_1 != '':
                                self.driver.find_element_by_xpath(
                                    '//div[@data-name="{}"]/span'.format(area_1)).click()
                            time.sleep(2)
                        except Exception as E:
                            logger.error(E)
                        try:
                            # 获取url节点
                            nodes = self.driver.find_elements_by_xpath('//div[@class="vm_product_wrap"]')
                            for node in nodes:
                                data_cid = node.get_attribute('data-cid')
                                data_pid = node.get_attribute('data-pid')
                                url = 'https://www.zdao.com/product/detail?' \
                                      + 'company_id=' + data_cid + '&product_id=' + data_pid
                                url_list.append(url)
                        except Exception as e:
                            print(e)
                            logger.error(e)
                            self.driver.refresh()
                            continue
                        try:
                            js = "var q=document.documentElement.scrollTop=100000"
                            self.driver.execute_script(js)
                            time.sleep(1)
                            self.driver.find_element_by_xpath(
                                '//div[@class="sg_next_page sg_page_item icon_chevron_right"]').click()
                        except Exception as e:
                            print(e)
                            logger.error(e)
                            break
                        time.sleep(2)
                    print(url_list)
                    # 遍历列表 请求url
                    for url in list(set(url_list)):
                        self.driver.get(url)
                        time.sleep(2)
                        print(url)
                        logger.info('当前详情url：%s' % url)
                        # 检测是否出现验证码
                        try:
                            self.check_YZM()
                            time.sleep(2)
                        except Exception as E:
                            print(E)
                            logger.error(E)
                        item = self.get_detail()
                        self.col.insert_one(item)
                        time.sleep(random.randint(1, 3))
                    self.driver.get(current_url)
                    time.sleep(2)
                break
            except Exception as e:
                print(e)
                logger.error(e)
                continue

    def get_detail(self):
        item = {}
        return item

    def run(self):
        """
        获取列表页、解析列表，详情页、完成退出
        :return:
        """
        self.get_list()
        self.parse_list()
        self.update_task()
        print('爬取完成')
