import random
import os
import re
from PIL import Image
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from utils.chaojiying import Chaojiying_Client
from db.base_spider import BaseSpider
from spider.models import *
from selenium.webdriver.chrome.options import Options


class QICHACHA(BaseSpider):
    def __init__(self, param):
        """
        初始化属性
        :param cookies: list
        :param table_name: str
        :param keyword_list: list 关键词列表
        """
        super(QICHACHA, self).__init__(param=param)
        self.username = param.get('username_qichacha')
        self.password = param.get('password_qichacha')
        self.table_name = param.get('table_name')
        self.accurate = param.get('accurate')
        self.type = param.get('type')
        chrome_options = Options()
        chrome_options.add_argument('window-size=1920x1800')  # 指定浏览器分辨率
        chrome_options.add_argument('--disable-gpu')  # 谷歌文档提到需要加上这个属性来规避bug
        chrome_options.add_argument('--hide-scrollbars')  # 隐藏滚动条, 应对一些特殊页面
        chrome_options.add_argument('--headless')  # 浏览器不提供可视化页面. linux下如果系统不支持可视化不加这条会启动失败
        self.driver = webdriver.Chrome(chrome_options=chrome_options)
        # self.driver = webdriver.Chrome()
        self.wait = WebDriverWait(self.driver, 5)

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

    def detail_yzm(self):
        """
        拖拽滑块，完成验证
        :return:
        """
        while True:
            slider = self.wait.until(EC.presence_of_element_located((By.XPATH, '//span[@id="nc_1_n1z"]')))
            time.sleep(1)
            try:
                ActionChains(self.driver).click_and_hold(slider).perform()
                time.sleep(1)
                for x in self.get_track(distance=350):
                    ActionChains(self.driver).move_by_offset(xoffset=x, yoffset=random.uniform(-2,  2)).perform()
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

    def yzm2(self):
        while True:
            imgelement = self.wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="nc_1__imgCaptcha_img"]/img')))
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
            size2 = imgelement2.size  #获取验证码的长宽
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

    def parse_list(self, url, search_company):
        """
        解析列表页，获取部分信息
        :param url: search  url
        :return: item（含部分信息）以及详情url
        """
        while True:
            self.driver.get(url)
            current_url = self.driver.current_url
            if 'login' in current_url:
                self.login()
                time.sleep(2)
            else:
                break
        time.sleep(2)
        try:
            self.detail_yzm()
        except Exception:
            pass
        try:
            nodes = self.wait.until(EC.presence_of_all_elements_located((By.XPATH, '//*[@id="searchlist"]//tbody/tr')))
            if len(nodes) == 0:
                detail_url = None
                item = None
                return detail_url, item
        except Exception as E:
            detail_url = None
            item = None
            return detail_url, item
        if not self.accurate:
            item = {}
            if self.type != '3':
                get_company = self.driver.find_element_by_xpath(
                        '//*[@id="searchlist"]//tr[1]/td[2]/a').text.replace('(', '（').replace(')', '）')
                item['search_company'] = search_company
                try:
                    item['company_name'] = get_company
                except:
                    item['company_name'] = ' '
                try:
                    item['another_name'] = self.driver.find_element_by_xpath(
                        '//*[@id="searchlist"]//tbody/tr[1]//i/..').text
                except:
                    item['another_name'] = ' '
                try:
                    item['company_url'] = self.driver.find_element_by_xpath(
                        '//*[@id="searchlist"]//tbody/tr[1]/td[2]/a').get_attribute('href')
                except:
                    item['company_url'] = ' '
                try:
                    item['telphone'] = self.driver.find_element_by_xpath('//*[@id="searchlist"]/table/tbody/tr[1]//span[contains(text(),"电话：")]').text.replace('电话：', '')
                except:
                    item['telphone'] = ' '
                try:
                    nodes = self.driver.find_elements_by_xpath('//*[@id="phoneModal"]/div/div/div[2]/div/div[1]')
                    item['tel_more'] = ';'.join([node.text for node in nodes])
                except:
                    item['tel_more'] = ' '
                try:
                    item['email'] = self.driver.find_element_by_xpath('//*[@id="searchlist"]/table/tbody/tr[1]//p[contains(text(),"邮箱：")]').text.strip().split(' ')[0].replace('邮箱：', '')
                except:
                    item['email'] = ' '
                try:
                    item['法定代表人'] = self.driver.find_element_by_xpath('//*[@id="searchlist"]/table/tbody/tr[1]/td[2]/p[1]').text.split('注册资本')[0].replace('法定代表人：', '').strip()
                except:
                    item['法定代表人'] = ' '
                try:
                    capital = self.driver.find_element_by_xpath('//*[@id="searchlist"]/table/tbody/tr[1]/td[2]/p[1]/span[1]').text.replace('注册资本：', '')
                    pattern = re.compile(r'(\d+\.?\d*)')
                    num = pattern.findall(capital)[0]
                    if '人民币' in capital:
                        item['注册资本'] = capital
                    elif '美元' in capital:
                        item['注册资本'] = capital.replace(num, str(int(num)*6.8)).replace('美元', '人民币')
                    elif '日元' in capital:
                        item['注册资本'] = capital.replace(num, str(int(num)*0.06)).replace('日元', '人民币')
                    elif '欧元' in capital:
                        item['注册资本'] = capital.replace(num, str(int(num)*7.9)).replace('欧元', '人民币')
                    elif '港元' in capital:
                        item['注册资本'] = capital.replace(num, str(int(num)*0.87)).replace('港元', '人民币')
                    elif '韩元' in capital:
                        item['注册资本'] = capital.replace(num, str(int(num)*0.006)).replace('韩元', '人民币')
                    elif '新加坡元' in capital:
                        item['注册资本'] = capital.replace(num, str(int(num)*5)).replace('新加坡元', '人民币')
                    elif '瑞士法郎' in capital:
                        item['注册资本'] = capital.replace(num, str(int(num)*6.9)).replace('瑞士法郎', '人民币')
                    elif '新台币' in capital:
                        item['注册资本'] = capital.replace(num, str(int(num)*0.22)).replace('新台币', '人民币')
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
                    item['成立时间'] = self.driver.find_element_by_xpath('//*[@id="searchlist"]/table/tbody/tr[1]/td[2]/p[1]/span[2]').text.replace('成立时间：', '').split('-')[0]
                except:
                    item['成立时间'] = ' '
                item['成立时间（new）'] = item['成立时间'] + '年'
                try:
                    item['公司地址'] = self.driver.find_element_by_xpath('//*[@id="searchlist"]/table/tbody/tr[1]/td[2]/p[3]').text.replace('地址：', '')
                except:
                    item['公司地址'] = ' '
                try:
                    item['状态'] = self.driver.find_element_by_xpath('//*[@id="searchlist"]/table/tbody/tr[1]/td[3]/span').text
                except:
                    item['状态'] = ' '
            detail_url = self.wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="searchlist"]/table/tbody/tr[1]/td[2]/a'))).get_attribute('href')
            return detail_url, item
        # 精准匹配
        if self.accurate == 'on':
            for node in nodes:
                company = node.find_element_by_xpath('./td[2]//a').text
                if search_company.replace('（', '(').replace('）', ')') == company.replace('（', '(').replace('）', ')'):
                    item = {}
                    if self.type != '3':
                        item['search_company'] = search_company
                        item['company_name'] = company.replace('(', '（').replace(')', '）')
                        try:
                            item['company_url'] = node.find_element_by_xpath(
                                './td[2]/a').get_attribute('href')
                        except:
                            item['company_url'] = ' '
                        try:
                            item['another_name'] = node.find_element_by_xpath(
                                './/i/..').text
                        except:
                            item['another_name'] = ' '
                        try:
                            item['telphone'] = node.find_element_by_xpath(
                                './/span[contains(text(),"电话：")]').text.strip().replace('电话：', '')
                        except:
                            item['telphone'] = ' '
                        try:
                            nodes = self.driver.find_elements_by_xpath('//*[@id="phoneModal"]/div/div/div[2]/div/div[1]')
                            item['tel_more'] = ';'.join([node.text for node in nodes])
                        except:
                            item['tel_more'] = ' '
                        try:
                            item['email'] = node.find_element_by_xpath(
                                './/p[contains(text(),"邮箱：")]').text.strip().replace('邮箱：', '')
                        except:
                            item['email'] = ' '
                        try:
                            item['法定代表人'] = node.find_element_by_xpath(
                                './td[2]/p[1]').text.split('注册资本')[0].replace('法定代表人：', '').strip()
                        except:
                            item['法定代表人'] = ' '
                        try:
                            item['注册资本'] = node.find_element_by_xpath(
                                './td[2]/p[1]/span[1]').text
                        except:
                            item['注册资本'] = ' '
                        try:
                            item['成立时间'] = node.find_element_by_xpath(
                                './td[2]/p[1]/span[2]').text
                        except:
                            item['成立时间'] = ' '
                        try:
                            item['公司地址'] = node.find_element_by_xpath(
                                './td[2]/p[3]').text.replace('地址：', '')
                        except:
                            item['公司地址'] = ' '
                        try:
                            item['状态'] = node.find_element_by_xpath(
                                './td[3]/span').text
                        except:
                            item['状态'] = ' '
                    detail_url = node.find_element_by_xpath('./td[2]/a').get_attribute('href')
                    return detail_url, item
            return None, None

    def parse_detail_all(self, detail_url, item):
        """
        请求详情页，并解析页面
        :param detail_url:
        :param item:
        :return: item 采集数据
        """
        while True:
            self.driver.get(detail_url)
            current_url = self.driver.current_url
            if 'login' in current_url:
                self.login()
                time.sleep(5)
            else:
                break
        time.sleep(5)
        try:
            self.detail_yzm()
        except:
            pass
        try:
            item['官网'] = self.driver.find_element_by_xpath('//span[text()="官网："]/following-sibling::span/a').get_attribute('href')
        except:
            item['官网'] = ' '
        try:
            item['上市'] = self.driver.find_element_by_xpath('//a[@data-original-title="查看上市详情"]').text
        except:
            item['上市'] = ' '
        try:
            item['法律诉讼'] = self.driver.find_element_by_xpath('//h2[text()="法律诉讼"]/../span').text
        except:
            item['法律诉讼'] = ' '
        try:
            item['实缴资本'] = self.driver.find_element_by_xpath('//*[@id="Cominfo"]/table[2]/tbody/tr[1]/td[4]').text
        except:
            item['实缴资本'] = ' '
        try:
            item['注册号'] = self.driver.find_element_by_xpath('//*[@id="Cominfo"]/table[2]/tbody/tr[4]/td[2]').text.strip()
        except:
            item['注册号'] = ' '
        try:
            item['公司类型'] = self.driver.find_element_by_xpath('//*[@id="Cominfo"]/table[2]/tbody/tr[5]/td[2]').text
        except:
            item['公司类型'] = ' '
        try:
            item['所属行业'] = self.driver.find_element_by_xpath('//*[@id="Cominfo"]/table[2]/tbody/tr[5]/td[4]').text
        except:
            item['所属行业'] = ' '
        try:
            item['核准日期'] = self.driver.find_element_by_xpath('//*[@id="Cominfo"]/table[2]/tbody/tr[6]/td[2]').text
        except:
            item['核准日期'] = ' '
        try:
            item['登记机关'] = self.driver.find_element_by_xpath('//*[@id="Cominfo"]/table[2]/tbody/tr[6]/td[4]').text
        except:
            item['登记机关'] = ' '
        try:
            item['所属地区'] = self.driver.find_element_by_xpath('//*[@id="Cominfo"]/table[2]/tbody/tr[7]/td[2]').text
        except:
            item['所属地区'] = ' '
        try:
            item['英文名'] = self.driver.find_element_by_xpath('//*[@id="Cominfo"]/table[2]/tbody/tr[7]/td[4]').text
        except:
            item['英文名'] = ' '
        try:
            item['曾用名'] = self.driver.find_element_by_xpath('//*[@id="Cominfo"]/table[2]/tbody/tr[8]/td[2]').text
        except:
            item['曾用名'] = ' '
        try:
            item['人员规模'] = self.driver.find_element_by_xpath('//*[@id="Cominfo"]/table[2]/tbody/tr[9]/td[2]').text
        except:
            item['人员规模'] = ' '
        try:
            item['经营范围'] = self.driver.find_element_by_xpath('//*[@id="Cominfo"]/table[2]/tbody/tr[11]/td[2]').text
        except:
            item['经营范围'] = ' '
        try:
            nodes = self.driver.find_elements_by_xpath('//*[@id="Sockinfo"]/table//tr')
            staff = ''
            for node in nodes[1:]:
                staff += node.find_element_by_xpath('./td[2]/a').text + ';'
            item['staff'] = staff
        except:
            item['staff'] = ' '
        try:
            self.driver.find_element_by_xpath('//span[text()="简介："]/following-sibling::span/a').click()
            time.sleep(3)
            item['公司简介'] = self.driver.find_element_by_xpath('//*[@id="jianjieModal"]//div[@class="modal body"]').text
            self.driver.find_element_by_xpath('//button[text()="确定"]').click()
            time.sleep(3)
        except:
            item['公司简介'] = ' '
        try:
            item['分支机构'] = self.driver.find_element_by_xpath('//*[@id="Subcom"]/div/span[1]').text
        except:
            item['分支机构'] = ' '
        try:
            self.wait.until(EC.presence_of_element_located((By.XPATH, '//a[@id="run_title"]'))).click()
            time.sleep(5)
        except Exception:
            pass
        try:
            item['融资日期'] = '-'.join(self.driver.find_element_by_xpath('//*[@id="financingList"]//tr[2]/td[2]').text.split('-')[0:2])
        except:
            item['融资日期'] = ' '
        try:
            item['融资级别'] = self.driver.find_element_by_xpath('//*[@id="financingList"]//tr[2]/td[4]').text
        except:
            item['融资级别'] = ' '
        try:
            item['融资金额'] = self.driver.find_element_by_xpath('//*[@id="financingList"]//tr[2]/td[5]').text
        except:
            item['融资金额'] = ' '
        try:
            item['招聘人数'] = self.driver.find_element_by_xpath('//h3[text()="招聘"]/../span[1]').text
        except:
            item['招聘人数'] = ' '
        try:
            item['最新职位'] = '-'.join(self.driver.find_element_by_xpath('//*[@id="joblist"]/table/tbody/tr[2]/td[2]').text.split('-')[0:2])
        except:
            item['最新职位'] = ' '
        try:
            item['实力等级'] = self.driver.find_element_by_xpath('//*[@id="V3_cwzl"]/table/tbody/tr[1]/td[2]').text
        except:
            item['实力等级'] = ' '
        try:
            item['纳税区间'] = self.driver.find_element_by_xpath('//*[@id="V3_cwzl"]/table/tbody/tr[1]/td[4]').text
        except:
            item['纳税区间'] = ' '
        try:
            item['销售净利润'] = self.driver.find_element_by_xpath('//*[@id="V3_cwzl"]/table/tbody/tr[2]/td[2]').text
        except:
            item['销售净利润'] = ' '
        try:
            item['销售毛利率'] = self.driver.find_element_by_xpath('//*[@id="V3_cwzl"]/table/tbody/tr[2]/td[4]').text
        except:
            item['销售毛利率'] = ' '
        return item

    def parse_detail_position(self, detail_url, company):
        url = detail_url + '#run'
        self.driver.get(url)
        time.sleep(5)
        try:
            self.detail_yzm()
        except Exception:
            pass
        try:
            catch_company = self.driver.find_element_by_xpath('//h1').text
        except:
            catch_company = self.driver.find_element_by_xpath('//div[@class="row title"]').text
        while True:
            if self.sign == 0:
                try:
                    nodes = self.driver.find_elements_by_xpath('//*[@id="joblist"]//tr')
                except:
                    return
                for node in nodes[1:]:
                    item= {}
                    item['输入公司名'] = company
                    item['采集公司名'] = catch_company.replace('(', '（').replace(')', '）')
                    try:
                        item['招聘职位'] = node.find_element_by_xpath('./td[3]').text.strip()
                    except:
                        item['招聘职位'] = ' '
                    try:
                        item['所在城市'] = node.find_element_by_xpath('./td[5]').text.strip()
                    except:
                        item['所在城市'] = ' '
                    try:
                        item['发布时间'] = node.find_element_by_xpath('./td[2]').text.strip()
                    except:
                        item['发布时间'] = ' '
                    try:
                        item['来源'] = node.find_element_by_xpath('./td[6]/a').text
                    except:
                        item['来源'] = ' '
                    item['date'] = int(time.time())
                    self.col.insert(item)
                try:
                    self.driver.find_element_by_xpath('//*[@id="joblist"]//a[text()=">"]').click()
                    time.sleep(5)
                except:
                    break
            else:
                break

    def parse_detail_litigation(self, detail_url, item):
        """
        请求详情页，并解析页面
        :param detail_url:
        :param item:
        :return: item 采集数据
        """
        while True:
            self.driver.get(detail_url)
            current_url = self.driver.current_url
            if 'login' in current_url:
                self.login()
                time.sleep(3)
            else:
                break
        time.sleep(5)
        try:
            self.detail_yzm()
        except Exception:
            pass
        try:
            self.driver.find_element_by_xpath('//h2[text()="法律诉讼"]/..').click()
        except:
            item['被执行人信息'] = ' '
            item['失信被执行人'] = ' '
            item['裁判文书'] = ' '
            item['法院公告'] = ' '
            item['开庭公告'] = ' '
            item['司法协助'] = ' '
            item['失信被执行人详情'] = ' '
            item['民事裁定书'] = ' '
            return item
        time.sleep(3)
        try:
            item['被执行人信息'] = self.driver.find_element_by_xpath('//div[@class="panel-body"]/a[contains(text(),"被执行人信息")]').text.strip().split(' ')[1]
        except:
            item['被执行人信息'] = ' '
        try:
            item['失信被执行人'] = \
            self.driver.find_element_by_xpath('//div[@class="panel-body"]/a[contains(text(),"失信被执行人")]').text.strip().split(
                ' ')[1]
        except:
            item['失信被执行人'] = ' '
        try:
            item['裁判文书'] = \
            self.driver.find_element_by_xpath('//div[@class="panel-body"]/a[contains(text(),"裁判文书")]').text.strip().split(
                ' ')[1]
        except:
            item['裁判文书'] = ' '
        try:
            item['法院公告'] = \
            self.driver.find_element_by_xpath('//div[@class="panel-body"]/a[contains(text(),"法院公告")]').text.strip().split(
                ' ')[1]
        except:
            item['法院公告'] = ' '
        try:
            item['开庭公告'] = \
            self.driver.find_element_by_xpath('//div[@class="panel-body"]/a[contains(text(),"开庭公告")]').text.strip().split(
                ' ')[1]
        except:
            item['开庭公告'] = ' '
        try:
            item['司法协助'] = \
                self.driver.find_element_by_xpath(
                    '//div[@class="panel-body"]/a[contains(text(),"司法协助")]').text.strip().split(
                    ' ')[1]
        except:
            item['司法协助'] = ' '
        try:
            nodes = self.driver.find_elements_by_xpath('//*[@id="shixinlist"]//td/a')
            if len(nodes) > 0:
                info = ''
                for node in nodes:
                    node.click()
                    time.sleep(2)
                    a = self.driver.find_element_by_xpath('//*[@id="relatList"]/table[1]//tr[6]/td[2]').text
                    b = self.driver.find_element_by_xpath('//*[@id="relatList"]/table[1]//tr[7]/td[2]').text
                    self.driver.find_element_by_xpath('//*[@id="RelatModal"]/div/div[1]/div[1]/button').click()
                    c = a + ':' + b
                    info += c + '|||||||||'
                    time.sleep(2)
                item['失信被执行人详情'] = info
            else:
                item['失信被执行人详情'] = ' '
        except:
            item['失信被执行人详情'] = ' '
        try:
            tds = self.driver.find_elements_by_xpath('//*[@id="wenshulist"]//td/a')
            if len(tds) > 0:
                for td in tds:
                    td.click()
                    time.sleep(2)
                    wenshu_ = self.driver.find_element_by_xpath('//*[@id="relatList"]').text
                    time.sleep(2)
                    self.driver.find_element_by_xpath('//*[@id="RelatModal"]/div/div[1]/div[1]/button').click()
                    time.sleep(2)
                    key = '民事裁定书' + str(tds.index(td))
                    item[key] = wenshu_
        except Exception:
            item['民事裁定书'] = ' '
        return item

    def login(self):
        self.driver.get('http://www.qichacha.com/user_login')
        time.sleep(3)
        # js = "document.getElementsByClassName('login-panel')[0].style.marginTop='-90px'"
        # self.driver.execute_script(js)
        self.wait.until(EC.presence_of_element_located((By.LINK_TEXT, '密码登录'))).click()
        self.wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="nameNormal"]'))).send_keys(self.username)
        self.wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="pwdNormal"]'))).send_keys(self.password)
        self.detail_yzm()
        self.driver.find_element_by_xpath('//*[@id="user_login_normal"]/button').click()
        time.sleep(2)

    def run(self):
        """
        执行过程
        :return:
        """
        try:
            self.login()
            for data in self.get_data():
                keyword = data['data']
                if self.sign == 0:
                    url = 'https://www.qichacha.com/search?key={}'.format(keyword)
                    detail_url, item = self.parse_list(url, keyword)
                    time.sleep(random.randint(15, 25))
                    if not detail_url and not item:
                        time.sleep(random.randint(15, 25))
                        self.finish_list.append(data['id'])
                        continue
                    if self.type == '0':
                        item = self.parse_detail_all(detail_url, item)
                    elif self.type == '1':
                        pass
                    elif self.type == '2':
                        item = self.parse_detail_litigation(detail_url, item)
                    elif self.type == '3':
                        self.parse_detail_position(detail_url, company=keyword)
                    if self.type != '3':
                        item['date'] = int(time.time())
                        self.col.insert_one(item)
                    self.finish_list.append(data['id'])
                    time.sleep(random.randint(15, 25))
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
        try:
            self.driver.quit()
        except:
            pass
