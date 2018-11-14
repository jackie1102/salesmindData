import os
import random
import re
from PIL import Image
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from utils.chaojiying import Chaojiying_Client
from selenium import webdriver
from selenium.webdriver import ActionChains
from db.base_spider import BaseSpider
from spider.models import *
import requests
from lxml import etree


class QiChaCha(BaseSpider):
    def __init__(self, param):
        super(QiChaCha, self).__init__(param=param)
        self.type = param.get('type')
        self.accurate = param.get('accurate')
        self.headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36',
        }

    def get_cookie(self):
        while True:
            try:
                r = requests.get('http://172.12.5.234:5000/qichacha/random')
                break
            except:
                continue
        content = r.text
        cookies = json.loads(content)
        return cookies

    def get_track(self, distance=300):
        """
        根据偏移量获取移动轨迹
        :param distance: 偏移量
        :return: 移动轨迹
        """
        # 移动轨迹
        track = []
        # 当前位移
        current = 0
        # 减速阈值
        mid = distance * 4 / 5
        # 计算间隔
        t = 0.2
        # 初速度
        v = 0
        while current < distance:
            if current < mid:
                # 加速度为正2
                a = random.randint(2, 5)
            else:
                # 加速度为负3
                a = -3
            # 初速度v0
            v0 = v
            # 当前速度v = v0 + at
            v = v0 + a * t
            # 移动距离x = v0t + 1/2 * a * t^2
            move = v0 * t + 1 / 2 * a * t * t
            # 当前位移
            current += move
            # 加入轨迹
            track.append(round(move))
        return track

    def detail_yzm(self, url):
        """
        拖拽滑块，完成验证
        :return:
        """
        chrome_options = Options()
        chrome_options.add_argument('window-size=1920x1800')  # 指定浏览器分辨率
        chrome_options.add_argument('--disable-gpu')  # 谷歌文档提到需要加上这个属性来规避bug
        chrome_options.add_argument('--hide-scrollbars')  # 隐藏滚动条, 应对一些特殊页面
        chrome_options.add_argument('--headless')  # 浏览器不提供可视化页面. linux下如果系统不支持可视化不加这条会启动失败
        self.driver = webdriver.Chrome(chrome_options=chrome_options)
        self.wait = WebDriverWait(self.driver, 10)
        self.driver.maximize_window()
        self.driver.get(url)
        while True:
            slider = self.wait.until(EC.presence_of_element_located((By.XPATH, '//span[@id="nc_1_n1z"]')))
            time.sleep(1)
            try:
                ActionChains(self.driver).click_and_hold(slider).perform()
                time.sleep(1)
                for x in self.get_track(distance=350):
                    ActionChains(self.driver).move_by_offset(xoffset=x, yoffset=random.uniform(-2, 2)).perform()
                time.sleep(0.5)
                ActionChains(self.driver).release().perform()
                time.sleep(1)
            except:
                continue
            try:
                self.driver.find_element_by_xpath('//*[@id="dom_id_one"]/div/span/a').click()
                time.sleep(0.5)
                continue
            except:
                break
        time.sleep(1)
        while True:
            try:
                try:
                    self.driver.find_element_by_xpath('//*[@id="nc_1_captcha_input"]').send_keys(1)
                    self.yzm2()
                    break
                except:
                    self.yzm1()
                    break
            except:
                break
        self.driver.quit()

    def yzm2(self):
        while True:
            imgelement = self.wait.until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="nc_1__imgCaptcha_img"]/img')))
            location = imgelement.location  # 获取滑条x,y轴坐标
            if location['x'] == 0:
                return
            self.driver.save_screenshot('qichacha.png')  # 截取当前网页，该网页有我们需要的验证码
            size = imgelement.size  # 获取滑条的长宽
            rangle = (int(location['x']), int(location['y']), int(location['x'] + size['width']),
                      int(location['y'] + size['height']))  # 写成我们需要截取的位置坐标
            i = Image.open("qichacha.png")  # 打开截图
            frame4 = i.crop(rangle)  # 使用Image的crop函数，从截图中再次截取我们需要的区域
            frame4.save('qichachayzm.png')
            chaojiying = Chaojiying_Client('jackie1102', 'salesmind1800', '1902')
            im = open('qichachayzm.png', 'rb').read()
            res = chaojiying.PostPic(im, 1902)
            pic_str = res['pic_str']
            os.remove("qichacha.png")
            os.remove("qichachayzm.png")
            inpt = self.driver.find_element_by_xpath('//*[@id="nc_1_captcha_input"]')
            inpt.clear()
            time.sleep(1)
            inpt.send_keys(pic_str)
            time.sleep(1)
            self.driver.find_element_by_xpath('//*[@id="nc_1_scale_submit"]/span').click()
            time.sleep(1)
            try:
                txt = self.driver.find_element_by_xpath('//*[@id="nc_1__captcha_img_text"]/span').text
                if txt:
                    chaojiying.ReportError(res['pic_id'])
                    time.sleep(2)
            except:
                break
        time.sleep(1)
        try:
            self.driver.find_element_by_xpath('//*[@id="verify"]').click()
            time.sleep(1)
        except:
            pass

    def yzm1(self):
        while True:
            # 定位滑条
            imgelement1 = self.wait.until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="nc_1__scale_text"]')))
            self.driver.save_screenshot('qichacha.png')  # 截取当前网页，该网页有我们需要的验证码
            location = imgelement1.location  # 获取滑条x,y轴坐标
            size1 = imgelement1.size  # 获取滑条的长宽
            # 定位验证码
            try:
                imgelement2 = self.driver.find_element_by_xpath('//*[@id="nc_1_clickCaptcha"]')
            except:
                return
            size2 = imgelement2.size  # 获取验证码的长宽
            rangle = (int(location['x']), int(location['y']), int(location['x'] + size1['width']),
                      int(location['y'] + size1['height'] + size2['height']))  # 写成我们需要截取的位置坐标
            i = Image.open("qichacha.png")  # 打开截图
            frame4 = i.crop(rangle)  # 使用Image的crop函数，从截图中再次截取我们需要的区域
            frame4.save('qichachayzm.png')
            chaojiying = Chaojiying_Client('jackie1102', 'salesmind1800', '9101')
            im = open('qichachayzm.png', 'rb').read()
            res = chaojiying.PostPic(im, 9101)
            content = res['pic_str']
            loca = content.split(',')
            action = ActionChains(self.driver)
            action.move_to_element_with_offset(imgelement1, int(loca[0]), int(loca[1]))
            action.click()
            action.perform()
            time.sleep(1)
            try:
                text = self.driver.find_element_by_xpath('//*[@id="nc_1__scale_text"]/span/b').text
                if text == '验证通过':
                    break
            except Exception:
                # print('验证失败')
                chaojiying.ReportError(res['pic_id'])
            time.sleep(1)
        try:
            self.driver.find_element_by_xpath('//*[@id="verify"]').click()
            time.sleep(1)
        except:
            pass

    def parse_check(self, data):
        """
        解析列表页
        :param data: 搜索公司名
        :return:
        """
        url = 'https://www.qichacha.com/search?key={}'.format(data)
        while True:
            try:
                r = requests.get(url, cookies=self.get_cookie(), headers=self.headers, timeout=5)
                txt = r.text
                if "<script>window.location.href=" in txt or 'var arg1=' in txt:
                    self.detail_yzm(url)
                    continue
                break
            except:
                continue
        html = etree.HTML(r.text)
        # 获取公司列表所有节点
        nodes = html.xpath('//*[@id="searchlist"]/table/tbody/tr')
        if len(nodes) == 0:
            return None, None
        # 精确查找
        if self.accurate == 'on':
            for node in nodes:
                company = ''.join(node.xpath('./td[2]/a//text()'))
                if data.replace('（', '(').replace('）', ')') == company.replace('（', '(').replace('）', ')'):
                    item = {}
                    item['搜索公司名'] = data
                    item['抓取公司名'] = company
                    try:
                        text = ''.join(node.xpath('.//i/..//text()'))
                        if '曾用名' in text:
                            item['anothername'] = text.replace('\n', '').replace('曾用名：', '').replace(' ', '')
                        else:
                            item['anothername'] = ' '
                    except:
                        item['anothername'] = ' '
                    try:
                        item['手机号'] = node.xpath('.//span[contains(text(),"电话：")]/text()')[0].replace('电话：', '')
                    except:
                        item['手机号'] = ' '
                    try:
                        item['邮箱'] = node.xpath('.//p[contains(text(),"邮箱：")]/text()')[0].replace('邮箱：', '').strip()
                    except:
                        item['邮箱'] = ' '
                    try:
                        item['法定代表人'] = ''.join(node.xpath('./td[2]/p[1]//text()')).split('注册资本')[0].replace('法定代表人：',
                                                                                                             '').strip().split(
                            '股本')[0].replace('董事长：', '').strip()
                    except:
                        item['法定代表人'] = ' '
                    try:
                        capital = node.xpath('./td[2]/p[1]/span[1]/text()')[0]
                        if '股本' in capital:
                            item['注册资本'] = capital
                        else:
                            capital = capital.replace('注册资本：', '')
                            pattern = re.compile(r'(\d+\.?\d*)')
                            num = pattern.findall(capital)[0]
                            if '人民币' in capital:
                                item['注册资本'] = capital
                            elif '美元' in capital:
                                item['注册资本'] = capital.replace(num, str(round(float(num) * 6.8, 4))).replace('美元',
                                                                                                             '人民币')
                            elif '日元' in capital:
                                item['注册资本'] = capital.replace(num, str(round(float(num) * 0.06, 4))).replace('日元',
                                                                                                              '人民币')
                            elif '欧元' in capital:
                                item['注册资本'] = capital.replace(num, str(round(float(num) * 7.9, 4))).replace('欧元',
                                                                                                             '人民币')
                            elif '港元' in capital:
                                item['注册资本'] = capital.replace(num, str(round(float(num) * 0.87, 4))).replace('港元',
                                                                                                              '人民币')
                            elif '韩元' in capital:
                                item['注册资本'] = capital.replace(num, str(round(float(num) * 0.006, 4))).replace('韩元',
                                                                                                               '人民币')
                            elif '新加坡元' in capital:
                                item['注册资本'] = capital.replace(num, str(round(float(num) * 5, 4))).replace('新加坡元',
                                                                                                           '人民币')
                            elif '瑞士法郎' in capital:
                                item['注册资本'] = capital.replace(num, str(round(float(num) * 6.9, 4))).replace('瑞士法郎',
                                                                                                             '人民币')
                            elif '新台币' in capital:
                                item['注册资本'] = capital.replace(num, str(round(float(num) * 0.22, 4))).replace('新台币',
                                                                                                              '人民币')
                            else:
                                item['注册资本'] = capital
                    except:
                        item['注册资本'] = ' '
                    pattern = re.compile(r'(\d+\.?\d*)')
                    if '股本' not in item['注册资本']:
                        n = pattern.findall(item['注册资本'])
                        if n:
                            item['注册资本（万）'] = n[0]
                        else:
                            item['注册资本（万）'] = ' '
                    else:
                        item['注册资本（万）'] = ' '
                    try:
                        item['成立时间'] = node.xpath('./td[2]/p[1]/span[2]/text()')[0].replace('成立时间：', '')
                    except:
                        item['成立时间'] = ' '
                    try:
                        item['公司地址'] = ''.join(node.xpath('./td[2]/p[3]//text()')).replace('地址：', '').strip()
                    except:
                        item['公司地址'] = ' '
                    try:
                        item['经营状态'] = node.xpath('./td[3]/span/text()')[0]
                    except:
                        item['经营状态'] = ' '
                    detail_url = 'https://www.qichacha.com' + node.xpath('./td[2]/a/@href')[0]
                    return detail_url, item
            else:
                return None, None
        else:
            # 抓取列表第一个
            nodes = html.xpath('//*[@id="searchlist"]/table/tbody/tr[1]')
            if nodes:
                node = nodes[0]
                item = {}
                item['搜索公司名'] = data
                item['抓取公司名'] = ''.join(node.xpath('./td[2]/a//text()'))
                try:
                    text = ''.join(node.xpath('.//i/..//text()'))
                    if '曾用名' in text:
                        item['anothername'] = text.replace('\n', '').replace('曾用名：', '').replace(' ', '')
                    else:
                        item['anothername'] = ' '
                except:
                    item['anothername'] = ' '
                try:
                    item['手机号'] = node.xpath('.//span[contains(text(),"电话：")]/text()')[0].replace('电话：', '')
                except:
                    item['手机号'] = ' '
                try:
                    item['邮箱'] = node.xpath('.//p[contains(text(),"邮箱：")]/text()')[0].replace('邮箱：', '').strip()
                except:
                    item['邮箱'] = ' '
                try:
                    item['法定代表人'] = \
                    ''.join(node.xpath('./td[2]/p[1]//text()')).split('注册资本')[0].replace('法定代表人：', '').strip().split(
                        '股本')[0].replace('董事长：', '').strip()
                except:
                    item['法定代表人'] = ' '
                try:
                    capital = node.xpath('./td[2]/p[1]/span[1]/text()')[0]
                    if '股本' in capital:
                        item['注册资本'] = capital
                    else:
                        capital = capital.replace('注册资本：', '')
                        pattern = re.compile(r'(\d+\.?\d*)')
                        num = pattern.findall(capital)[0]
                        if '人民币' in capital:
                            item['注册资本'] = capital
                        elif '美元' in capital:
                            item['注册资本'] = capital.replace(num, str(round(float(num) * 6.8, 4))).replace('美元', '人民币')
                        elif '日元' in capital:
                            item['注册资本'] = capital.replace(num, str(round(float(num) * 0.06, 4))).replace('日元', '人民币')
                        elif '欧元' in capital:
                            item['注册资本'] = capital.replace(num, str(round(float(num) * 7.9, 4))).replace('欧元', '人民币')
                        elif '港元' in capital:
                            item['注册资本'] = capital.replace(num, str(round(float(num) * 0.87, 4))).replace('港元', '人民币')
                        elif '韩元' in capital:
                            item['注册资本'] = capital.replace(num, str(round(float(num) * 0.006, 4))).replace('韩元', '人民币')
                        elif '新加坡元' in capital:
                            item['注册资本'] = capital.replace(num, str(round(float(num) * 5, 4))).replace('新加坡元', '人民币')
                        elif '瑞士法郎' in capital:
                            item['注册资本'] = capital.replace(num, str(round(float(num) * 6.9, 4))).replace('瑞士法郎', '人民币')
                        elif '新台币' in capital:
                            item['注册资本'] = capital.replace(num, str(round(float(num) * 0.22, 4))).replace('新台币', '人民币')
                        else:
                            item['注册资本'] = capital
                except:
                    item['注册资本'] = ' '
                pattern = re.compile(r'(\d+\.?\d*)')
                if '股本' not in item['注册资本']:
                    n = pattern.findall(item['注册资本'])
                    if n:
                        item['注册资本（万）'] = n[0]
                    else:
                        item['注册资本（万）'] = ' '
                else:
                    item['注册资本（万）'] = ' '
                try:
                    item['成立时间'] = node.xpath('./td[2]/p[1]/span[2]/text()')[0].replace('成立时间：', '')
                except:
                    item['成立时间'] = ' '
                try:
                    item['公司地址'] = ''.join(node.xpath('./td[2]/p[3]//text()')).replace('地址：', '').strip()
                except:
                    item['公司地址'] = ' '
                try:
                    item['经营状态'] = node.xpath('./td[3]/span/text()')[0]
                except:
                    item['经营状态'] = ' '
                detail_url = 'https://www.qichacha.com' + node.xpath('./td[2]/a/@href')[0]
                return detail_url, item
            else:
                return None, None

    def parse_all(self, url, item):
        """
        解析详情页
        :param url: 详情url
        :param item: 解析列表页生成的数据字典
        :return:
        """
        while True:
            try:
                r = requests.get(url, cookies=self.get_cookie(), headers=self.headers, timeout=5)
                txt = r.text
                if "<script>window.location.href=" in txt or 'var arg1=' in txt:
                    self.detail_yzm(url)
                    continue
                break
            except:
                continue
        current_url = r.url
        html = etree.HTML(r.text)
        try:
            item['官方网站'] = html.xpath('//span[@class="cvlu webauth"]/a[1]/@href')[0]
        except:
            item['官方网站'] = ' '
        try:
            item['上市信息'] = html.xpath('//h3[@class="nlisted-title"]/text()')[0].replace(' ', '')
        except:
            item['上市信息'] = ' '
        try:
            item['法律诉讼'] = html.xpath('//h2[text()="法律诉讼"]/../span/text()')[0]
        except:
            item['法律诉讼'] = ' '
        try:
            item['实缴资本'] = html.xpath('//td[text()="实缴资本："]/following-sibling::td/text()')[0].strip()
        except:
            item['实缴资本'] = ' '
        try:
            item['注册号'] = html.xpath('//td[text()="注册号："]/following-sibling::td/text()')[0].strip()
        except:
            item['注册号'] = ' '
        try:
            item['公司类型'] = html.xpath('//td[text()="公司类型："]/following-sibling::td/text()')[0].strip()
        except:
            item['公司类型'] = ' '
        try:
            item['所属行业'] = html.xpath('//td[text()="所属行业："]/following-sibling::td/text()')[0].strip()
        except:
            item['所属行业'] = ' '
        try:
            item['核准日期'] = html.xpath('//td[text()="核准日期："]/following-sibling::td/text()')[0].strip()
        except:
            item['核准日期'] = ' '
        try:
            item['登记机关'] = html.xpath('//td[text()="登记机关"]/following-sibling::td/text()')[0].strip()
        except:
            item['登记机关'] = ' '
        try:
            item['所属地区'] = html.xpath('//td[text()="所属地区："]/following-sibling::td/text()')[0].strip()
        except:
            item['所属地区'] = ' '
        try:
            item['英文名'] = html.xpath('//td[text()="英文名："]/following-sibling::td/text()')[0].strip()
        except:
            item['英文名'] = ' '
        try:
            item['曾用名'] = ';'.join(
                html.xpath('//td[contains(text(),"曾用名")]/following-sibling::td//span/text()')).strip().replace('\xa0',
                                                                                                               '')
        except:
            item['曾用名'] = ' '
        try:
            item['人员规模'] = html.xpath('//td[contains(text(),"人员规模")]/following-sibling::td/text()')[0].strip()
        except:
            item['人员规模'] = ' '
        try:
            item['经营范围'] = html.xpath('//td[text()="经营范围："]/following-sibling::td/text()')[0].strip()
        except:
            item['经营范围'] = ' '
        try:
            item['股东信息'] = ';'.join(html.xpath('//*[@id="Sockinfo"]/table//tr//h3/text()'))
        except:
            item['股东信息'] = ' '
        try:
            item['公司简介'] = ''.join(html.xpath('//*[@id="jianjieModal"]//div[@class="modal-body"]//text()')).replace(' ',
                                                                                                                    '')
        except:
            item['公司简介'] = ' '
        try:
            item['分支机构'] = ''.join(html.xpath('//*[@id="Subcom"]/div/span[1]/text()'))[0]
        except:
            item['分支机构'] = ' '
        company = item['抓取公司名']
        unique = current_url.split('firm_')[-1].replace('.html', '')
        # 解析经营状况
        time.sleep(0.2)
        item = self.parse_run(unique, company, item)
        return item

    def parse_run(self, unique, company, item):
        """
        解析经营状况
        :param unique:
        :param company:
        :param item:
        :return:
        """
        url = 'https://www.qichacha.com/company_getinfos?unique={}&companyname={}&tab=run'.format(unique, company)
        while True:
            try:
                r = requests.get(url, cookies=self.get_cookie(), headers=self.headers, timeout=5)
                txt = r.text
                if "<script>window.location.href=" in txt or 'var arg1=' in txt:
                    self.detail_yzm(url)
                    continue
                break
            except:
                continue
        html = etree.HTML(r.text)
        try:
            item['融资日期'] = html.xpath('//*[@id="financingList"]//tr[1]/td[2]/text()')[0]
        except:
            item['融资日期'] = ' '
        try:
            item['融资级别'] = html.xpath('//*[@id="financingList"]//tr[1]/td[4]/text()')[0]
        except:
            item['融资级别'] = ' '
        try:
            item['融资金额'] = html.xpath('//*[@id="financingList"]//tr[1]/td[5]/text()')[0]
        except:
            item['融资金额'] = ' '
        try:
            item['招聘人数'] = html.xpath('//h3[text()="招聘"]/../span[1]/text()')[0]
        except:
            item['招聘人数'] = ' '
        try:
            item['最新职位发布日期'] = html.xpath('//*[@id="joblist"]/table/tbody/tr[2]/td[2]/text()')[0].strip()
        except:
            item['最新职位发布日期'] = ' '
        try:
            item['实力等级'] = html.xpath('//td[contains(text(),"实力等级")]/following-sibling::td[1]/text()')[0]
        except:
            item['实力等级'] = ' '
        try:
            item['纳税区间'] = html.xpath('//td[contains(text(),"纳税区间")]/following-sibling::td[1]/text()')[0]
        except:
            item['纳税区间'] = ' '
        try:
            item['销售净利润'] = html.xpath('//td[contains(text(),"销售净利润")]/following-sibling::td[1]/text()')[0]
        except:
            item['销售净利润'] = ' '
        try:
            item['销售毛利率'] = html.xpath('//td[contains(text(),"销售毛利率")]/following-sibling::td[1]/text()')[0]
        except:
            item['销售毛利率'] = ' '
        return item

    def parse_detail_position(self, unique, company):
        """
        :param detail_url:
        :param company:
        :return:
        """
        url = 'https://www.qichacha.com/company_getinfos?unique=' + unique + '&companyname=' + company + '&p={}&tab=run&box=job'
        while True:
            page = 1
            while True:
                try:
                    r = requests.get(url.format(page), cookies=self.get_cookie(), headers=self.headers, timeout=5)
                    txt = r.text
                    if "<script>window.location.href=" in txt or 'var arg1=' in txt:
                        self.detail_yzm(url)
                        continue
                    break
                except:
                    continue
            html = etree.HTML(r.text)
            nodes = html.xpath('//tr')
            for node in nodes[1:]:
                item = {}
                item['输入公司名'] = company
                try:
                    item['招聘职位'] = node.xpath('./td[3]/a/text()')[0].strip()
                except:
                    item['招聘职位'] = ' '
                try:
                    item['所在城市'] = node.xpath('./td[7]/text()')[0].strip()
                except:
                    item['所在城市'] = ' '
                try:
                    item['发布时间'] = node.xpath('./td[2]/text()')[0].strip()
                except:
                    item['发布时间'] = ' '
                item['date'] = int(time.time())
                self.col.insert(item)
            next = html.xpath('//a[text()=">"]')
            if next:
                page += 1
                time.sleep(0.5)
            else:
                break

    def parse_detail_litigation(self, unique, company):
        url = 'https://www.qichacha.com/company_getinfos?unique={}&companyname={}&tab=susong'.format(unique, company)
        while True:
            try:
                r = requests.get(url, cookies=self.get_cookie(), headers=self.headers, timeout=5)
                txt = r.text
                if "<script>window.location.href=" in txt or 'var arg1=' in txt:
                    self.detail_yzm(url)
                    continue
                break
            except:
                continue
        html = etree.HTML(r.text)
        item = {}
        try:
            item['被执行人信息'] = html.xpath('//a[contains(text(),"被执行人信息")]/text()')[0].strip().split('\xa0')[1]
        except:
            item['被执行人信息'] = ' '
        try:
            item['失信被执行人'] = html.xpath('//a[contains(text(),"失信被执行人")]/text()')[0].strip().split('\xa0')[1]
        except:
            item['失信被执行人'] = ' '
        try:
            item['裁判文书'] = html.xpath('//a[contains(text(),"裁判文书")]/text()')[0].strip().split('\xa0')[1]
        except:
            item['裁判文书'] = ' '
        try:
            item['法院公告'] = html.xpath('//a[contains(text(),"法院公告")]/text()')[0].strip().split('\xa0')[1]
        except:
            item['法院公告'] = ' '
        try:
            item['开庭公告'] = html.xpath('//a[contains(text(),"开庭公告")]/text()')[0].strip().split('\xa0')[1]
        except:
            item['开庭公告'] = ' '
        try:
            item['司法协助'] = html.xpath('//a[contains(text(),"司法协助")]/text()')[0].strip().split('\xa0')[1]
        except:
            item['司法协助'] = ' '
        nodes = html.xpath('//*[@id="shixinlist"]//a/@onclick')
        if nodes:
            info = ''
            for node in nodes:
                shixin_id = node.split('","')[1].replace('")', '')
                c = self.parse_shixin(shixin_id)
                info += c + '|||||||||||||||'
                time.sleep(1)
            item['失信被执行人详情'] = info.replace('\n', '')
        else:
            item['失信被执行人详情'] = ' '
        nodes = html.xpath('//*[@id="wenshulist"]//td/a/@onclick')
        if nodes:
            for node in nodes:
                wenshu_id = node.split('","')[1].replace('")', '')
                text = self.parse_wenshu(wenshu_id)
                key = '民事裁定书' + str(nodes.index(node))
                item[key] = text.replace('\u3000', '')
                time.sleep(0.5)
        else:
            item['民事裁定书'] = ' '
        return item

    def parse_shixin(self, id):
        url = 'https://www.qichacha.com/company_shixinRelat?id={}'.format(id)
        while True:
            try:
                r = requests.get(url, cookies=self.get_cookie(), headers=self.headers, timeout=5)
                txt = r.text
                if "<script>window.location.href=" in txt or 'var arg1=' in txt:
                    self.detail_yzm(url)
                    continue
                break
            except:
                continue
        html = etree.HTML(r.text)
        # 失信被执行人行为具体情形
        try:
            a = html.xpath('//tr[6]/td[2]/text()')[0]
        except:
            a = ' '
        # 生效法律文书确定的义务
        try:
            b = html.xpath('//tr[7]/td[2]/text()')[0]
        except:
            b = ' '
        c = a + ':' + b
        return c

    def parse_wenshu(self, id):
        url = 'https://www.qichacha.com/company_wenshuRelat?id={}'.format(id)
        while True:
            try:
                r = requests.get(url, cookies=self.get_cookie(), headers=self.headers, timeout=5)
                txt = r.text
                if "<script>window.location.href=" in txt or 'var arg1=' in txt:
                    self.detail_yzm(url)
                    continue
                break
            except:
                time.sleep(1)
                continue
        html = etree.HTML(r.text)
        text = ''.join(html.xpath('//div[@class="wenshu-view"]//text()')).replace(' ', '')
        return text

    def run(self):
        try:
            for data in self.get_data():
                if self.sign == 0:
                    detail, item = self.parse_check(data['data'])
                    time.sleep(0.5)
                    if detail:
                        unique = detail.split('firm_')[-1].replace('.html', '')
                        if self.type == '0':
                            item = self.parse_all(detail, item)
                            time.sleep(0.5)
                        elif self.type == '1':
                            pass
                        elif self.type == '2':
                            item = self.parse_detail_litigation(unique, item['抓取公司名'])
                            time.sleep(0.5)
                        elif self.type == '3':
                            self.parse_detail_position(unique, item['抓取公司名'])
                            time.sleep(0.5)
                        if self.type != '3':
                            item['date'] = int(time.time())
                            self.col.insert_one(item)
                    self.finish_list.append(data['id'])

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
