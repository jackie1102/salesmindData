from selenium.webdriver.chrome.options import Options
from spider.models import *
import random
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from PIL import Image
from utils.chaojiying import Chaojiying_Client
import time
from db.base_spider import BaseSpider


class Job51(BaseSpider):
    def __init__(self, param):
        super(Job51, self).__init__(param=param)
        self.vipname = param.get('membername_job51')
        self.username = param.get('username_job51')
        self.password = param.get('password_job51')
        self.type = param.get('type')
        chrome_options = Options()
        chrome_options.add_argument('window-size=1920x3000')  # 指定浏览器分辨率
        chrome_options.add_argument('--disable-gpu')  # 谷歌文档提到需要加上这个属性来规避bug
        chrome_options.add_argument('--hide-scrollbars')  # 隐藏滚动条, 应对一些特殊页面
        chrome_options.add_argument('--headless')  # 浏览器不提供可视化页面. linux下如果系统不支持可视化不加这条会启动失败
        self.driver = webdriver.Chrome(chrome_options=chrome_options)
        # self.driver = webdriver.Chrome()
        self.driver.maximize_window()
        self.wait = WebDriverWait(self.driver, 3)

    def login(self):
        self.driver.get('https://ehire.51job.com/')
        js1 = "document.getElementsByClassName('headerBanner')[0].style.display='none'"
        js2 = "document.getElementsByClassName('topHeader')[0].style.display='none'"
        self.driver.execute_script(js1)
        self.driver.execute_script(js2)
        self.wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="txtMemberNameCN"]'))).send_keys(
            self.vipname)
        self.wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="txtUserNameCN"]'))).send_keys(self.username)
        self.wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="txtPasswordCN"]'))).send_keys(self.password)
        self.wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="btnBeginValidate"]'))).click()
        while True:
            time.sleep(1)
            imgelement = self.driver.find_element_by_xpath('//*[@id="divValidateHtml"]/div')  # 定位验证码
            self.driver.save_screenshot('aa.png')  # 截取当前网页，该网页有我们需要的验证码
            location = imgelement.location  # 获取验证码x,y轴坐标
            print(location)
            if location['x'] == 0:
                return
            size = imgelement.size  # 获取验证码的长宽
            print(size['width'])
            rangle = (int(location['x']), int(location['y']), int(location['x'] + size['width']),
                      int(location['y'] + size['height']))  # 写成我们需要截取的位置坐标
            i = Image.open("aa.png")  # 打开截图
            frame4 = i.crop(rangle)  # 使用Image的crop函数，从截图中再次截取我们需要的区域
            frame4.save('frame4.png')
            chaojiying = Chaojiying_Client('jackie1102', 'salesmind1800', '9004')
            im = open('frame4.png', 'rb').read()
            while True:
                try:
                    res = chaojiying.PostPic(im, 9004)
                except Exception as E:
                    print(E)
                    time.sleep(2)
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
                action.pause(1)
            action.perform()
            time.sleep(1)
            self.wait.until(EC.presence_of_element_located((By.LINK_TEXT, '验 证'))).click()
            time.sleep(1)
            success = self.driver.find_element_by_xpath('//*[@id="btnEndValidate"]').text
            if success == '验证通过':
                break
            else:
                chaojiying.ReportError(res['pic_id'])
                time.sleep(3)
        self.driver.find_element_by_xpath('//*[@id="Login_btnLoginCN"]').click()

    def check_yzm(self):
        """
         验证码处理：
        1·捕获验证码，对当前页面进行截屏
        2·定位验证码图片位置，并从截屏中提取
        3·调用打码平台，破解验证码，返回验证码参数
        4·对验证码参数进一步处理，并模拟人工操作破解验证码
        5·验证是否破解成功，否则发送验证失败api
        :return:
        """
        while True:
            try:
                imgelement = self.driver.find_element_by_xpath('//*[@id="divValidateHtml"]/div')  # 定位验证码
                self.driver.save_screenshot('aa.png')  # 截取当前网页，该网页有我们需要的验证码
                location = imgelement.location  # 获取验证码x,y轴坐标
                if location['x'] == 0:
                    return
                size = imgelement.size  # 获取验证码的长宽
                rangle = (int(location['x']), int(location['y']), int(location['x'] + size['width']),
                          int(location['y'] + size['height']))  # 写成我们需要截取的位置坐标
                i = Image.open("aa.png")  # 打开截图
                frame4 = i.crop(rangle)  # 使用Image的crop函数，从截图中再次截取我们需要的区域
                frame4.save('frame4.png')
                chaojiying = Chaojiying_Client('jackie1102', 'salesmind1800', '9004')
                im = open('frame4.png', 'rb').read()
                while True:
                    try:
                        res = chaojiying.PostPic(im, 9004)
                    except Exception as E:
                        print(E)
                        time.sleep(2)
                        continue
                    break
                content = res['pic_str'].split('|')
                print(res)
                loc_list = []
                for i in content:
                    loc = i.split(',')
                    loc_list.append(loc)
                action = ActionChains(self.driver)
                for loca in loc_list:
                    action.move_to_element_with_offset(imgelement, int(loca[0]), int(loca[1])).click()
                    action.pause(1)
                action.perform()
                time.sleep(1)
                self.wait.until(EC.presence_of_element_located((By.LINK_TEXT, '验 证'))).click()
                time.sleep(1)
                self.driver.refresh()
                imgelement = self.driver.find_element_by_xpath('//*[@id="divValidateHtml"]/div')  # 定位验证码
                print(imgelement, '111111')
                self.driver.save_screenshot('d://aa.png')  # 截取当前网页，该网页有我们需要的验证码
                location = imgelement.location  # 获取验证码x,y轴坐标
                print(location)
                if location['x'] == 0:
                    print('验证成功')
                else:
                    print('验证失败')
                    chaojiying.ReportError(res['pic_id'])
                time.sleep(3)
            except:
                print('没有出现验证码')
                break

    def parse_list(self):
        self.driver.get('https://ehire.51job.com/InboxResume/CompanyHRDefault2.aspx?Page=2&belong=3')
        time.sleep(2)
        self.check_yzm()
        time.sleep(0.3)
        self.wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="txt_posttime"]'))).click()
        self.wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="divdrop_posttime"]/a[@value="0"]'))).click()
        self.wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="div_searchlist"]/dl[1]/dd/div/a'))).click()
        self.wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="dic_keyword_{}"]'.format(self.type)))).click()
        time.sleep(1)
        for ID in self.get_data():
            self.check_yzm()
            if self.sign == 0:
                node = self.driver.find_element_by_xpath('//*[@id="CandidateFolder_txt_keyword"]')
                node.clear()
                time.sleep(0.3)
                if ID['data']:
                    node.send_keys(ID['data'])
                    time.sleep(0.3)
                else:
                    self.finish_list.append(ID['id'])
                    continue
                time.sleep(1)
                self.driver.find_element_by_xpath('//*[@id="div_searchlist"]/dl[4]/dd/div[1]/a').click()
                self.check_yzm()
                try:
                    nodes = self.wait.until(
                        EC.presence_of_all_elements_located((By.XPATH, '//tr[contains(@id,"trBaseInfo")]')))
                except:
                    nodes = []
                if not nodes:
                    self.finish_list.append(ID['id'])
                    continue
                detail_list = []
                for node in nodes:
                    detail = node.find_element_by_xpath('.//a[@class="a_username"]').get_attribute('href')
                    detail_list.append(detail)
                js = 'window.open("https://www.baidu.com/");'
                self.driver.execute_script(js)
                handles = self.driver.window_handles
                for handle in handles:  # 切换窗口
                    if handle != self.driver.current_window_handle:
                        self.driver.switch_to.window(handle)
                for detail in detail_list:
                    self.driver.get(detail)
                    item = self.parse_detail()
                    self.col.insert_one(item)
                    time.sleep(random.randint(2, 3))
                self.finish_list.append(ID['id'])
                self.driver.close()
                self.driver.switch_to.window(handles[0])
            else:
                break

    def parse_detail(self):
        self.check_yzm()
        item = {}
        url = self.driver.current_url
        try:
            item['ID'] = self.driver.find_element_by_xpath('//span[contains(text(), "ID:")]').text.strip().replace('ID:', '')
        except:
            item['ID'] = ' '
        try:
            item['updatetime'] = self.wait.until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="lblResumeUpdateTime"]'))).text
        except:
            item['updatetime'] = '-'
        try:
            item['目前状况'] = self.driver.find_element_by_xpath('//table[@class="infr"]//tr[2]//tr/td[1]').text
        except:
            item['目前状况'] = '-'
        try:
            item['姓名'] = self.driver.find_element_by_xpath('//td[@class="name"]').text.strip().split('-')[0]
        except:
            item['姓名'] = '-'
        try:
            item['手机'] = self.driver.find_element_by_xpath('//table[@class="infr"]//tr[2]//tr/td[2]').text
        except:
            item['手机'] = '-'
        try:
            item['邮箱'] = self.driver.find_element_by_xpath('//a[@class="blue"]').text
        except:
            item['邮箱'] = '-'
        try:
            item['职位'] = self.driver.find_element_by_xpath('//td[text()="职　位："]/following-sibling::td').text
        except:
            item['职位'] = '-'
        try:
            item['公司'] = self.driver.find_element_by_xpath('//td[text()="公　司："]/following-sibling::td').text
        except:
            item['公司'] = '-'
        try:
            item['工作时间'] = self.driver.find_elements_by_xpath('//td[@class="time"]')[0].text
        except:
            item['工作时间'] = '-'
        try:
            item['工作描述'] = self.driver.find_element_by_xpath(
                '//td[text()="工作经验"]/../../tr[2]//tbody/tr[1]//tbody/tr[4]//tr/td[2]').text
        except:
            item['工作描述'] = '-'
        item['date'] = int(time.time())
        return item

    def run(self):
        try:
            self.login()
            self.parse_list()
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
            self.driver.get('https://ehire.51job.com/LoginOut.aspx')
            time.sleep(1)
        except:
            pass
        finally:
            self.driver.quit()
