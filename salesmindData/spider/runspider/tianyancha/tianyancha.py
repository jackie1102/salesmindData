import random
import requests
from selenium.webdriver import ActionChains
from utils.chaojiying import Chaojiying_Client
from PIL import Image
from lxml import etree
from db.base_spider import BaseSpider
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from spider.models import *
from selenium.webdriver.chrome.options import Options


headers = {}


class TianYanCha(BaseSpider):

    def __init__(self, param):
        """
        初始化属性
        :param param:
        :param data_list:
        """
        super(TianYanCha, self).__init__(param=param)
        self.username = param.get('username_tianyancha')
        self.password = param.get('password_tianyancha')
        self.session = requests.session()

    def parse_list(self, company):
        """
        解析列表页
        :param company:
        :return:
        """
        while True:
            r = self.session.get('https://www.tianyancha.com/search?key={}'.format(company), headers=headers)
            # print(r.url)
            html = etree.HTML(r.content.decode())
            if 'antirobot' in r.url:
                    self.yzm()
            else:
                break
        try:
            node = html.xpath('//div[contains(@class,"search-result-single")]')[0]
            item = {}
            item['经营状态'] = node.xpath('.//div[contains(@class,"statusTypeNor")]/text()')[0]
            item['法人'] = node.xpath('.//div[text()="法定代表人："]/a/text()')[0]
            data = node.xpath('.//div[text()="注册资本："]/span/text()')[0]
            item['注册资本'] = data
            date = node.xpath('.//div[text()="注册时间："]/span/text()')[0]
            item['注册时间'] = date
            try:
                item['联系电话'] = node.xpath('.//span[text()="联系电话："]/../span[2]/text()')[0]
            except:
                item['联系电话'] = ' '
            item['地区'] = node.xpath('.//span[@class="float-right search-right-center"]/text()')[0]
            item['分数'] = node.xpath('.//span[@class="c9 f20"]/text()')[0]
            item['详情链接'] = node.xpath('.//a[contains(@class,"sv-search-company")]/@href')[0]
            return item
        except:
            return None

    def parse_detail(self, item):
        """
        解析详情页
        :param item:
        :return:
        """
        while True:
            detail_url = item['详情链接']
            r = self.session.get(detail_url, headers=headers)
            html = etree.HTML(r.content.decode())
            if 'antirobot' in r.url:
                    self.yzm()
            else:
                break
        try:
            item['公司名'] = html.xpath('//h1/text()')[0]
        except:
            item['公司名'] = ' '
        try:
            item['邮箱'] = html.xpath('//span[text()="邮箱："]/../span[2]/text()')[0]
        except:
            item['邮箱'] = ' '
        try:
            item['网址'] = html.xpath('//span[text()="网址："]/../a/@href')[0]
        except:
            item['网址'] = ' '
        try:
            item['详细地址'] = html.xpath('//span[text()="地址："]/../span[2]/text()')[0]
        except:
            item['详细地址'] = ' '
        try:
            item['公司简介'] = html.xpath(
                '//*[@id="company_base_info_detail"]/text()')[0].replace('\t', '').replace('\n', '').replace(' ', '')
        except:
            item['公司简介'] = ' '
        try:
            item['公司类型'] = html.xpath('//td[text()="公司类型"]/following-sibling::td[1]/text()')[0]
        except:
            item['公司类型'] = ' '
        try:
            item['行业'] = html.xpath('//td[text()="行业"]/following-sibling::td[1]/text()')[0]
        except:
            item['行业'] = ' '
        try:
            item['注册地址'] = html.xpath('//td[text()="注册地址"]/following-sibling::td[1]/text()')[0]
        except:
            item['注册地址'] = ' '
        try:
            item['经营范围'] = html.xpath(
                '//td[text()="经营范围"]/following-sibling::td[1]//span[@class="js-full-container"]/text()')[0]
        except:
            item['经营范围'] = ' '
        try:
            item['注册地址'] = html.xpath('//td[text()="注册地址"]/following-sibling::td[1]/text()')[0]
        except:
            item['注册地址'] = ' '
        try:
            item['招聘'] = html.xpath('//*[@id="nav-main-recruitCount"]/span/text()')[0]
        except:
            item['招聘'] = ' '
        try:
            item['股东信息'] = ''
            nodes = html.xpath('//*[@id="_container_holder"]//tbody//tr')
            for node in nodes:
                name = node.xpath('./td[1]/a/text()')[0]
                Proportion = node.xpath('./td[2]//span/text()')[0]
                m = name + '>' + Proportion + '|'
                item['股东信息'] += m
        except:
            item['股东信息'] = ' '
        try:
            Rz_time = html.xpath('//*[@id="_container_rongzi"]//tbody/tr[1]/td[1]/span/text()')[0]
            Rz_lunci = html.xpath('//*[@id="_container_rongzi"]//tbody/tr[1]/td[2]/span/text()')[0]
            Rz_jine = html.xpath('//*[@id="_container_rongzi"]//tbody/tr[1]/td[4]/span/text()')[0]
            item['融资信息'] = Rz_time + '>' + Rz_lunci + '>' + Rz_jine
        except:
            item['融资信息'] = ' '
        try:
            item['企业业务_产品名'] = html.xpath(
                '//*[@id="_container_firmProduct"]//div[@class="product-right"]/div[1]/span/text()')[0]
        except:
            item['企业业务_产品名'] = ' '
        try:
            item['企业业务_类型'] = html.xpath(
                '//*[@id="_container_firmProduct"]//div[@class="product-right"]/div[2]/text()')[0]
        except:
            item['企业业务_类型'] = ' '
        try:
            item['企业业务_主营'] = html.xpath(
                '//*[@id="_container_firmProduct"]//div[@class="product-right"]/div[3]/text()')[0]
        except:
            item['企业业务_主营'] = ' '
        try:
            item['网站备案'] = ''
            icp_nodes = html.xpath('//*[@id="_container_icp"]//tbody/tr')
            for icp_node in icp_nodes:
                icpname = icp_node.xpath('./td[2]/span/text()')[0]
                icp_website = icp_node.xpath('./td[3]/a/@href')[0]
                icp_m = icpname + ':' + icp_website + '|'
                item['网站备案'] += icp_m
        except:
            item['网站备案'] = ' '
        # print(item)
        return item

    def login(self):
        """
        模拟登陆，获取cookie
        :return:
        """
        chrome_options = Options()
        chrome_options.add_argument('window-size=1920x3000')  # 指定浏览器分辨率
        chrome_options.add_argument('--disable-gpu')  # 谷歌文档提到需要加上这个属性来规避bug
        chrome_options.add_argument('--hide-scrollbars')  # 隐藏滚动条, 应对一些特殊页面
        chrome_options.add_argument('--headless')  # 浏览器不提供可视化页面. linux下如果系统不支持可视化不加这条会启动失败
        self.driver = webdriver.Chrome(chrome_options=chrome_options)
        self.wait = WebDriverWait(self.driver, 10)
        self.driver.get('https://www.tianyancha.com/login')
        username = self.wait.until(
                EC.presence_of_element_located((By.XPATH, '//div[contains(@class,"modulein1")]//input[@type="text"]')))
        username.clear()
        username.send_keys(self.username)
        password = self.wait.until(
                EC.presence_of_element_located((
                    By.XPATH, '//div[contains(@class,"modulein1")]//input[@type="password"]')))
        password.clear()
        password.send_keys(self.password)
        self.wait.until(
            EC.presence_of_element_located((
                By.XPATH, '//div[contains(@class,"modulein1")]//div[text()="登录"]'))).click()
        while True:
            current_url = self.driver.current_url
            if current_url == 'https://www.tianyancha.com/':
                break
            else:
                time.sleep(1)
        # 将cookie转化为requests可用的cookie形式
        cookie = [item["name"] + "=" + item["value"] for item in self.driver.get_cookies()]
        cookiestr = ';'.join(item for item in cookie)
        global headers
        headers = {
            'Host': 'www.tianyancha.com',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36',
            'Cookie': cookiestr,
            'Referer': 'https://www.tianyancha.com/'
        }
        return self.driver

    def yzm(self):
        """
        浏览器模拟登陆处理验证码
        :return:
        """
        driver = self.login()
        driver.get('https://antirobot.tianyancha.com/captcha/verify?')
        time.sleep(2)
        while True:
            try:
                imgelement = self.driver.find_element_by_xpath('//div[@class="new-box94"]')  # 定位验证码
                self.driver.save_screenshot('tianyancha.png')  # 截取当前网页，该网页有我们需要的验证码
                location = imgelement.location  # 获取验证码x,y轴坐标
                if location['x'] == 0:
                    return
                size = imgelement.size  # 获取验证码的长宽
                # print(size['width'])
                rangle = (int(location['x']), int(location['y']), int(location['x'] + size['width']),
                          int(location['y'] + size['height']))  # 写成我们需要截取的位置坐标
                i = Image.open("tianyancha.png")  # 打开截图
                frame4 = i.crop(rangle)  # 使用Image的crop函数，从截图中再次截取我们需要的区域
                frame4.save('frame_tyc.png')
                chaojiying = Chaojiying_Client('jackie1102', 'salesmind1800', '9004')
                im = open('frame_tyc.png', 'rb').read()
                while True:
                    try:
                        res = chaojiying.PostPic(im, 9004)
                    except Exception as E:
                        # print(E)
                        continue
                    break
                content = res['pic_str'].split('|')
                loc_list = []
                for i in content:
                    loc = i.split(',')
                    loc_list.append(loc)
                action = ActionChains(self.driver)
                for loca in loc_list:
                    action.move_to_element_with_offset(imgelement, int(loca[0]), int(loca[1])).click()
                action.perform()
                time.sleep(1)
                self.wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="submitie"]'))).click()
                time.sleep(1)
                self.driver.refresh()
                imgelement = self.driver.find_element_by_xpath('//div[@class="new-box94"]')  # 定位验证码
                location = imgelement.location  # 获取验证码x,y轴坐标
                if location['x'] == 0:
                    # print('验证成功')
                    break
                else:
                    # print('验证失败')
                    chaojiying.ReportError(res['pic_id'])
            except Exception:
                break
        driver.quit()

    def run(self):
        """
        执行过程
        :return:
        """
        try:
            driver = self.login()
            driver.quit()
            for data in self.get_data():
                company = data['data']
                if self.sign == 0:
                    item = self.parse_list(company)
                    if item and self.sign == 0:
                        item = self.parse_detail(item)
                        item['输入公司名'] = company
                        item['date'] = int(time.time())
                        self.col.insert_one(item)
                    self.finish_list.append(data['id'])
                    time.sleep(random.randint(15, 20))
                else:
                    break
            if self.sign == 0:
                SpiderTask.objects.finish_task2(task_id=self.task_id)
                print('{}已完成'.format(self.table_name))
            else:
                print('{}已中断'.format(self.table_name))
        except Exception as E:
            print(E)
            SpiderTask.objects.change_task2_status(task_id=self.task_id)
            print('{}已中断'.format(self.table_name))


