import random
import requests
from PIL import Image
from selenium import webdriver
from db.base_spider import BaseSpider
from spider.models import *
from utils.chaojiying import Chaojiying_Client
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from spider.runspider.zhaopin_.phone_code import PhoneCode


class BaseZhaoPin(BaseSpider):
    """
    连接数据库
    """
    def __init__(self, param):
        """
        初始化属性
        """
        super(BaseZhaoPin,self).__init__(param=param)
        self.param = param
        self.get_cookie()

    def get_cookie(self):
        while True:
            users = ZhiLianId.objects.get_data_list_by_status(0)
            if users:
                self.user = random.choice(users)
                self.username = self.user.username
                self.password = self.user.password
                self.username_id = self.user.id
                cookie = self.login()
                task = SpiderTask.objects.get_one_task(id=self.task_id)
                data = json.loads(task.param)
                data["login_cookie"] = cookie
                data['username_id'] = self.username_id
                task.param = json.dumps(data)
                task.save()
                self.headers = {
                    'Cookie': cookie,
                    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'
                }
                break
            else:
                time.sleep(300)
        self.user.status = 1
        self.user.task_id = self.task_id
        self.user.save()

    def get_access_token(self):
        # 获取access_token
        auth_url = 'http://ihr.zhaopin.com/api/user/authLogin.do'
        response = requests.get(url=auth_url, headers=self.headers)
        a = response.text
        a = json.loads(a)
        access_token = a['data']['token']
        return access_token

    def login(self):
        """
        登录网站
        :return:
        """
        options = webdriver.FirefoxOptions()
        options.add_argument('-headless')
        options.add_argument('--disable-gpu')
        driver = webdriver.Firefox(firefox_options=options)
        # driver = webdriver.Firefox()
        driver.maximize_window()
        wait = WebDriverWait(driver, 5)
        driver.get('https://passport.zhaopin.com/org/login')
        time.sleep(2)
        wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="loginName"]'))).send_keys(self.username)
        time.sleep(2)
        wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="password"]'))).send_keys(self.password)
        time.sleep(2)
        while True:
            wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="loginbutton"]'))).click()
            time.sleep(2)
            imgelement = wait.until(
                EC.presence_of_element_located((By.XPATH, '//div[@class="geetest_head"]')))  # 定位验证码
            location1 = imgelement.location  # 获取验证码x,y轴坐标
            if location1['x'] == 0:
                continue
            else:
                break
        while True:
            imgelement1 = wait.until(
                  EC.presence_of_element_located((By.XPATH, '//div[@class="geetest_head"]')))  # 定位验证码
            imgelement2 = wait.until(
                EC.presence_of_element_located((By.XPATH, '//div[@class="geetest_table_box"]')))  # 定位验证码
            location1 = imgelement1.location  # 获取验证码x,y轴坐标
            if location1['x'] == 0:
                break
            driver.save_screenshot('aa.png')  # 截取当前网页，该网页有我们需要的验证码
            size1 = imgelement1.size  # 获取验证码的长宽
            size2 = imgelement2.size  # 获取验证码的长宽
            rangle = (int(location1['x']), int(location1['y']), int(location1['x'] + size1['width']),
                      int(location1['y'] + size1['height']+ size2['height']))  # 写成我们需要截取的位置坐标
            i = Image.open("aa.png")  # 打开截图
            frame4 = i.crop(rangle)  # 使用Image的crop函数，从截图中再次截取我们需要的区域
            frame4.save('frame4.png')
            chaojiying = Chaojiying_Client('jackie1102', 'salesmind1800', '9004')
            im = open('frame4.png', 'rb').read()
            res = chaojiying.PostPic(im, 9004)
            content = res['pic_str'].split('|')
            print(res)
            loc_list = []
            for i in content:
                loc = i.split(',')
                loc_list.append(loc)
            action = ActionChains(driver)
            loc1 = loc_list[0]
            try:
                x = int(loc1[0])
            except Exception as E:
                print(E)
                chaojiying.ReportError(res['pic_id'])
                continue
            for loca in loc_list:
                action.move_to_element_with_offset(imgelement1, int(loca[0]), int(loca[1])).click()
                action.pause(random.uniform(1, 2))
            action.perform()
            time.sleep(1)
            wait.until(EC.presence_of_element_located((By.XPATH, '//a[@class="geetest_commit"]'))).click()
            time.sleep(2)
            try:
                imgelement = wait.until(EC.presence_of_element_located((
                    By.XPATH, '//div[@class="geetest_widget"]')))
                location = imgelement.location
                if location['x'] == 0:
                    break
                else:
                    chaojiying.ReportError(res['pic_id'])
                    time.sleep(1)
                    continue
            except:
                break
        try:
            input_phone = driver.find_element_by_xpath('//*[@id="vmobile"]')
            pc = PhoneCode()
            phone = pc.get_phone()
            input_phone.send_keys(phone)
            driver.find_element_by_xpath('//a[@class="verify_code_btn"]').click()
            while True:
                imgelement1 = wait.until(
                    EC.presence_of_element_located((By.XPATH, '//div[@class="geetest_head"]')))  # 定位验证码
                imgelement2 = wait.until(
                    EC.presence_of_element_located((By.XPATH, '//div[@class="geetest_table_box"]')))  # 定位验证码
                driver.save_screenshot('aa.png')  # 截取当前网页，该网页有我们需要的验证码
                location1 = imgelement1.location  # 获取验证码x,y轴坐标
                print(location1)
                if location1['x'] == 0:
                    break
                size1 = imgelement1.size  # 获取验证码的长宽
                size2 = imgelement2.size  # 获取验证码的长宽
                print(size1['width'])
                rangle = (int(location1['x']), int(location1['y']), int(location1['x'] + size1['width']),
                          int(location1['y'] + size1['height'] + size2['height']))  # 写成我们需要截取的位置坐标
                i = Image.open("aa.png")  # 打开截图
                frame4 = i.crop(rangle)  # 使用Image的crop函数，从截图中再次截取我们需要的区域
                frame4.save('frame4.png')
                chaojiying = Chaojiying_Client('jackie1102', 'salesmind1800', '9004')
                im = open('frame4.png', 'rb').read()
                res = chaojiying.PostPic(im, 9004)
                content = res['pic_str'].split('|')
                print(res)
                loc_list = []
                for i in content:
                    loc = i.split(',')
                    loc_list.append(loc)
                action = ActionChains(driver)
                loc1 = loc_list[0]
                try:
                    x = int(loc1[0])
                except Exception as E:
                    print(E)
                    chaojiying.ReportError(res['pic_id'])
                    continue
                for loca in loc_list:
                    action.move_to_element_with_offset(imgelement1, int(loca[0]), int(loca[1])).click()
                    action.pause(random.uniform(1, 2))
                action.perform()
                time.sleep(1)
                wait.until(EC.presence_of_element_located((By.XPATH, '//a[@class="geetest_commit"]'))).click()
                time.sleep(2)
                try:
                    imgelement = wait.until(EC.presence_of_element_located((
                        By.XPATH, '//div[@class="geetest_widget"]')))
                    location = imgelement.location
                    if location['x'] == 0:
                        break
                    else:
                        chaojiying.ReportError(res['pic_id'])
                        time.sleep(1)
                        continue
                except:
                    break
            code = pc.get_code(phone)
            input_code = driver.find_element_by_xpath('//*[@id="verifyCode"]')
            input_code.send_keys(code)
            driver.find_element_by_xpath('//*[@id="confirm_btn"]').click()
        except:
            pass
        time.sleep(5)
        cookie = [item["name"] + "=" + item["value"] for item in driver.get_cookies()]
        cookiestr = '; '.join(item for item in cookie)
        print(cookiestr)
        driver.quit()
        return cookiestr

    def release(self):
        user = ZhiLianId.objects.get_one_ID_by_id(self.username_id)
        user.status = 0
        user.task_id = 0
        user.save()
        task = SpiderTask.objects.get_one_task(id=self.task_id)
        data = json.loads(task.param)
        data["login_cookie"] = ''
        data['username_id'] = ''
        task.param = json.dumps(data)
        task.save()



