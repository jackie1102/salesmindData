import json
from selenium import webdriver
import requests
import time
from lxml import etree
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait


class ITJUZI(object):
    def __init__(self, param):
        """
        初始化属性
        :param table_name: 数据库表名
        :param scope: int 行业
        :param sub_scope: int 子行业
        :param fund_status: int 轮次状态
        :param prov: str 地区
        :param stage: int 阶段
        :param fund_needs: int 融资需求
        :param born_year: int 成立时间
        :param status: int 运营状态
        :param page: int 页码
        """
        self.base_url = 'https://www.itjuzi.com/company?'
        industry = param.get('industry')
        if industry and '/' in industry:
            self.scope = '&scope={}'.format(industry.split('/')[0])
            self.sub_scope = '&sub_scope={}'.format(industry.split('/')[1])
        if industry and '/' not in industry:
            self.scope = '&scope={}'.format(industry)
        self.fund_status = '&fund_status={}'.format(param.get('state_cast')) if param.get('state_cast') else ''
        self.prov = '&prov={}'.format(param.get('area')) if param.get('area') else ''
        self.stage = '&stage={}'.format(param.get('stage')) if param.get('stage') else ''
        self.fund_needs = '&fund_needs={}'.format(param.get('financing_demand')) if param.get('financing_demand') else ''
        self.born_year = '&born_year={}'.format(param.get('establish_time')) if param.get('establish_time') else ''
        self.status = '&status={}'.format(param.get('state')) if param.get('state') else ''
        self.page = '&page={}'.format(param.get('design_page')) if param.get('design_page') else ''

    def get_headers_proxy(self):
        """
        更换IP 重新登陆
        获取新的cookie
        :return:
        """
        while True:
            res = requests.get('http://api.xdaili.cn/xdaili-api//privateProxy/getDynamicIP/DD20181265614RYXDKJ/74a9b61350c811e79d9b7cd30abda612?returnType=2')
            content = res.content.decode()
            print(content)
            ipdict = json.loads(content)
            ip = ipdict.get('RESULT')
            ip_address = 'http://' + ip.get('wanIp') + ':' + ip.get('proxyport')
            proxy = {
                'http': ip_address,
                'https': ip_address,
            }
            chrome_options = webdriver.ChromeOptions()
            chrome_options.add_argument('--proxy-server={}'.format(ip_address))
            driver = webdriver.Chrome(chrome_options=chrome_options)
            wait = WebDriverWait(driver, 20)
            try:
                driver.get('https://www.itjuzi.com/user/login')
                time.sleep(1)
                wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="create_account_email"]'))).send_keys('aven.wang@outlook.com')
                time.sleep(1)
                wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="create_account_password"]'))).send_keys('342740')
                time.sleep(1)
                wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="login_btn"]'))).submit()
                time.sleep(2)
                cookie = [item["name"] + "=" + item["value"] for item in driver.get_cookies()]
                cookiestr = ';'.join(item for item in cookie)
                print(cookiestr)
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.108 Safari/537.36',
                    'Cookie': cookiestr,
                    'Host': 'www.itjuzi.com'
                }
                self.headers = headers
                self.proxy = proxy
                driver.quit()
                break
            except Exception as E:
                print(E)
                driver.quit()
                time.sleep(15)
                continue

    def mosaic_url(self):
        """
        根据条件拼接url
        :param num:
        :return: 拼接后的url
        """
        url_ = self.base_url + self.scope + self.sub_scope + self.fund_status + self.prov + \
                     self.stage + self.fund_needs + self.born_year + self.status
        search_url = url_.replace('{}', '').replace('?&', '?').replace(',', '').replace('不限', '')
        return search_url

    def parse_page(self, url):
        """
        请求拼接好的url
        获取详情页url
        :param url: 拼接好的url
        :return: 详情页url 列表
        """
        session = requests.session()
        r = session.get(url=url, headers=self.headers, proxies=self.proxy, timeout=30).content.decode()
        selector = etree.HTML(r)
        url_list = []
        try:
            nodes = selector.xpath('//ul[@class="list-main-icnset company-list-ul"]/li')
            for _ in nodes:
                href = _.xpath('div[@class="cell maincell"]/div[@class="title"]/a/@href')[0]
                url_list.append(href)
        except Exception as E:
            print(E)
        return url_list

    def page_details(self, url):
        """
        解析详情页
        :param url: 详情页url
        :return: 抓取的数据
        """
        session = requests.session()
        r = session.get(url, headers=self.headers, proxies=self.proxy, timeout=30).content.decode()
        # r = session.get(url, headers=self.headers, timeout=30).text
        selector = etree.HTML(r)
        item = {}
        for _ in selector.xpath('//div[@class="picinfo"]'):
            short_name = _.xpath('div[@class="line-title"]/span[@class="title"]/h1/@data-name')
            short_name = ''.join(str(i).strip() for i in short_name)
            full_name = _.xpath('div[@class="line-title"]/span[@class="title"]/h1/@data-fullname')
            full_name = ''.join(str(i).strip() for i in full_name)
            slogan = _.xpath('div[2]/h2/text()')
            slogan = ''.join(str(i).strip() for i in slogan)
            link = _.xpath('div[@class="link-line"]/a/@href')
            link = ''.join(str(i) for i in link)
            # print(short_name, full_name, slogan)
            item.update({'short_name': short_name, 'full_name': full_name, 'slogan': slogan, 'link': link})
        # name=selector.xpath('//div[@class="line-title"]/span[@class="title"]/h1')
        for _ in selector.xpath('//div[@class="block-inc-info on-edit-hide"]'):
            brief_intro = _.xpath(
                'div[@class="block" and position()=1]/div/descendant::text()|div[@class="block"]/div[@class="summary"]/text()')
            brief_intro = ''.join(str(i).strip() for i in brief_intro)
            establish_time = _.xpath(
                'div[@class="block" and position()=2]/div/h3[1]/descendant::text()|div[@class="block"]/div/h3[1]/descendant::text()')
            establish_time = ''.join(str(i).strip() for i in establish_time)
            scale = _.xpath('div[@class="block"]/div/h3[2]/descendant::text()')
            scale = ''.join(str(i).strip() for i in scale)
            # print(brief_intro, establish_time, scale)
            item.update({'brief_intro': brief_intro, 'establish_time': establish_time, 'scale': scale})
        for _ in selector.xpath('//ul[@class="contact-list limited-itemnum"]/li/ul'):
            phone = _.xpath('li[contains(i/@class,"fa icon icon-phone-o")]/span/text()')
            phone = ''.join(str(i) for i in phone)
            mail = _.xpath('li[contains(i/@class,"fa icon icon-email-o")]/span/text()')
            mail = ''.join(str(i) for i in mail)
            location = _.xpath('li[contains(i/@class,"fa icon icon-address-o")]/span/text()')
            location = ''.join(str(i) for i in location)
            # print({'phone': phone, 'mail': mail, 'location': location})
            item.update({'phone': phone, 'mail': mail, 'location': location})
        for _ in selector.xpath('//table[@class="list-round-v2"]/tbody/tr'):
            ficancing_time = _.xpath('td[1]/span/text()')
            ficancing_time = ''.join(str(i).strip() for i in ficancing_time)
            rounds = _.xpath('td[2]/span/a/text()')
            rounds = ''.join(str(i).strip() for i in rounds)
            leadership = selector.xpath('//li[@class="feedback-btn-parent first-letter-box-4js"]/div/descendant::text()')
            leadership = ''.join(str(i).strip() for i in leadership)
            item.update({'financing_time': ficancing_time, 'rounds': rounds, 'leadership': leadership})
        self.col.insert(item)
        return item

    def run(self):
        """
        执行过程
        :return:
        """
        search_url = self.mosaic_url()
        self.get_headers_proxy()
        page = int(self.page) if self.page and self.page != '' else 1
        while True:
            try:
                url = search_url + '&page={}'.format(page)
                print('搜索URL：', url)
                while True:
                    try:
                        url_list = self.parse_page(url)
                        break
                    except Exception as E:
                        print(E)
                        self.get_headers_proxy()
                        time.sleep(0.5)
                        continue
                if len(url_list) != 0:
                    for i in url_list:
                        print('详情URL：', i)
                        while True:
                            try:
                                print(self.page_details(i))
                                break
                            except requests.RequestException as E:
                                print(E)
                                self.get_headers_proxy()
                                time.sleep(0.5)
                                continue
                        time.sleep(3)
                else:
                    break
            except requests.RequestException as E:
                print(E)
                print('当前页码为：', page)
                self.get_headers_proxy()
                continue
            page += 1

