import os
import random
from selenium.webdriver.chrome.options import Options
from PIL import Image
from selenium import webdriver
from db.base_spider import BaseSpider
from spider.models import *
from utils.chaojiying import Chaojiying_Client
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from salesmindData.settings import BASE_DIR


class BaseJob(BaseSpider):
    """
    连接数据库
    """

    def __init__(self, param):
        """
        初始化属性
        """
        super(BaseJob, self).__init__(param=param)
        self.param = param
        self.get_cookie()

    def get_cookie(self):
        while True:
            users = JobId.objects.get_data_list_by_status(0)
            if users:
                self.user = random.choice(users)
                self.vipname = self.user.vipname
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

    def login(self):
        """
        登录网站
        :return:
        """
        chrome_options = Options()
        chrome_options.add_argument('window-size=1920x1500')  # 指定浏览器分辨率
        chrome_options.add_argument('--disable-gpu')  # 谷歌文档提到需要加上这个属性来规避bug
        chrome_options.add_argument('--hide-scrollbars')  # 隐藏滚动条, 应对一些特殊页面
        chrome_options.add_argument('--headless')  # 浏览器不提供可视化页面. linux下如果系统不支持可视化不加这条会启动失败
        # driver = webdriver.Chrome()
        driver = webdriver.Chrome(chrome_options=chrome_options)
        driver.maximize_window()
        wait = WebDriverWait(driver, 5)
        driver.get('https://ehire.51job.com/')
        time.sleep(1)
        while True:
            wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="txtMemberNameCN"]'))).send_keys(
                self.vipname)
            wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="txtUserNameCN"]'))).send_keys(
                self.username)
            wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="txtPasswordCN"]'))).send_keys(
                self.password)
            wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="btnBeginValidate"]'))).click()
            time.sleep(1)
            while True:
                imgelement = driver.find_element_by_xpath('//*[@id="divValidateHtml"]/div')  # 定位验证码
                location = imgelement.location  # 获取验证码x,y轴坐标
                if location['x'] == 0:
                    return
                driver.save_screenshot(BASE_DIR + '/' + self.table_name + '_job.png')  # 截取当前网页，该网页有我们需要的验证码
                size = imgelement.size  # 获取验证码的长宽
                rangle = (int(location['x']), int(location['y']), int(location['x'] + size['width']),
                          int(location['y'] + size['height']))  # 写成我们需要截取的位置坐标
                i = Image.open(BASE_DIR + '/' + self.table_name + '_job.png')  # 打开截图
                frame = i.crop(rangle)  # 使用Image的crop函数，从截图中再次截取我们需要的区域
                frame.save(BASE_DIR + '/' + self.table_name + 'frame.png')
                chaojiying = Chaojiying_Client('jackie1102', 'salesmind1800', '9004')
                im = open(BASE_DIR + '/' + self.table_name + 'frame.png', 'rb').read()
                while True:
                    try:
                        res = chaojiying.PostPic(im, 9004)
                    except Exception as E:
                        time.sleep(2)
                        continue
                    break
                os.remove(BASE_DIR + '/' + self.table_name + '_job.png')
                os.remove(BASE_DIR + '/' + self.table_name + 'frame.png')
                content = res['pic_str'].split('|')
                loc_list = []
                for i in content:
                    loc = i.split(',')
                    loc_list.append(loc)
                action = ActionChains(driver)
                for loca in loc_list:
                    action.move_to_element_with_offset(imgelement, int(loca[0]), int(loca[1])).click()
                action.perform()
                time.sleep(1)
                wait.until(EC.presence_of_element_located((By.LINK_TEXT, '验 证'))).click()
                time.sleep(1)
                success = driver.find_element_by_xpath('//*[@id="btnEndValidate"]').text
                if success == '验证通过':
                    break
                else:
                    chaojiying.ReportError(res['pic_id'])
                    time.sleep(3)
            driver.find_element_by_xpath('//*[@id="Login_btnLoginCN"]').click()
            try:
                wait.until(EC.presence_of_element_located((By.XPATH, '//a[text()="强制下线"]'))).click()
                time.sleep(2)
                url = driver.current_url
                if 'Navigate.aspx?' in url:
                    break
                else:
                    continue
            except:
                break
        time.sleep(5)
        cookie = [item["name"] + "=" + item["value"] for item in driver.get_cookies()]
        cookiestr = '; '.join(item for item in cookie)
        print(cookiestr)
        driver.quit()
        return cookiestr

    def release(self):
        user = JobId.objects.get_one_ID_by_id(self.username_id)
        user.status = 0
        user.task_id = 0
        user.save()
        task = SpiderTask.objects.get_one_task(id=self.task_id)
        data = json.loads(task.param)
        data["login_cookie"] = ''
        data['username_id'] = ''
        task.param = json.dumps(data)
        task.save()

    def check_YZM(self, html, url):
        node = ''.join(html.xpath('//*[@id="Head1"]/title/text()')).strip()
        if '简历' not in node:
            chrome_options = Options()
            chrome_options.add_argument('window-size=1920x1500')  # 指定浏览器分辨率
            chrome_options.add_argument('--disable-gpu')  # 谷歌文档提到需要加上这个属性来规避bug
            chrome_options.add_argument('--hide-scrollbars')  # 隐藏滚动条, 应对一些特殊页面
            chrome_options.add_argument('--headless')  # 浏览器不提供可视化页面. linux下如果系统不支持可视化不加这条会启动失败
            # driver = webdriver.Chrome()
            driver = webdriver.Chrome(chrome_options=chrome_options)
            driver.maximize_window()
            wait = WebDriverWait(driver, 5)
            driver.get('https://ehire.51job.com/')
            time.sleep(1)
            while True:
                wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="txtMemberNameCN"]'))).send_keys(
                    self.vipname)
                wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="txtUserNameCN"]'))).send_keys(
                    self.username)
                wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="txtPasswordCN"]'))).send_keys(
                    self.password)
                wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="btnBeginValidate"]'))).click()
                time.sleep(1)
                while True:
                    imgelement = driver.find_element_by_xpath('//*[@id="divValidateHtml"]/div')  # 定位验证码
                    location = imgelement.location  # 获取验证码x,y轴坐标
                    if location['x'] == 0:
                        return
                    driver.save_screenshot(BASE_DIR + '/' + self.table_name + '_job.png')  # 截取当前网页，该网页有我们需要的验证码
                    size = imgelement.size  # 获取验证码的长宽
                    rangle = (int(location['x']), int(location['y']), int(location['x'] + size['width']),
                              int(location['y'] + size['height']))  # 写成我们需要截取的位置坐标
                    i = Image.open(BASE_DIR + '/' + self.table_name + '_job.png')  # 打开截图
                    frame = i.crop(rangle)  # 使用Image的crop函数，从截图中再次截取我们需要的区域
                    frame.save(BASE_DIR + '/' + self.table_name + 'frame.png')
                    chaojiying = Chaojiying_Client('jackie1102', 'salesmind1800', '9004')
                    im = open(BASE_DIR + '/' + self.table_name + 'frame.png', 'rb').read()
                    while True:
                        try:
                            res = chaojiying.PostPic(im, 9004)
                        except Exception as E:
                            time.sleep(2)
                            continue
                        break
                    os.remove(BASE_DIR + '/' + self.table_name + '_job.png')
                    os.remove(BASE_DIR + '/' + self.table_name + 'frame.png')
                    content = res['pic_str'].split('|')
                    loc_list = []
                    for i in content:
                        loc = i.split(',')
                        loc_list.append(loc)
                    action = ActionChains(driver)
                    for loca in loc_list:
                        action.move_to_element_with_offset(imgelement, int(loca[0]), int(loca[1])).click()
                    action.perform()
                    time.sleep(1)
                    wait.until(EC.presence_of_element_located((By.LINK_TEXT, '验 证'))).click()
                    time.sleep(1)
                    success = driver.find_element_by_xpath('//*[@id="btnEndValidate"]').text
                    if success == '验证通过':
                        break
                    else:
                        chaojiying.ReportError(res['pic_id'])
                        time.sleep(3)
                driver.find_element_by_xpath('//*[@id="Login_btnLoginCN"]').click()
                try:
                    wait.until(EC.presence_of_element_located((By.XPATH, '//a[text()="强制下线"]'))).click()
                    time.sleep(2)
                    url_ = driver.current_url
                    if 'Navigate.aspx?' in url_:
                        break
                    else:
                        continue
                except:
                    break
            """
             验证码处理：
            1·捕获验证码，对当前页面进行截屏
            2·定位验证码图片位置，并从截屏中提取
            3·调用打码平台，破解验证码，返回验证码参数
            4·对验证码参数进一步处理，并模拟人工操作破解验证码
            5·验证是否破解成功，否则发送验证失败api
            :return:
            """
            driver.get(url)
            time.sleep(2)
            while True:
                try:
                    imgelement = driver.find_element_by_xpath('//*[@id="divValidateHtml"]/div')  # 定位验证码
                    location = imgelement.location  # 获取验证码x,y轴坐标
                    if location['x'] == 0:
                        break
                    driver.save_screenshot(BASE_DIR + '/' + self.table_name + '_job.png')  # 截取当前网页，该网页有我们需要的验证码
                    size = imgelement.size  # 获取验证码的长宽
                    rangle = (int(location['x']), int(location['y']), int(location['x'] + size['width']),
                              int(location['y'] + size['height']))  # 写成我们需要截取的位置坐标
                    i = Image.open(BASE_DIR + '/' + self.table_name + '_job.png')  # 打开截图
                    frame = i.crop(rangle)  # 使用Image的crop函数，从截图中再次截取我们需要的区域
                    frame.save(BASE_DIR + '/' + self.table_name + 'frame.png')
                    chaojiying = Chaojiying_Client('jackie1102', 'salesmind1800', '9004')
                    im = open(BASE_DIR + '/' + self.table_name + 'frame.png', 'rb').read()
                    while True:
                        try:
                            res = chaojiying.PostPic(im, 9004)
                        except Exception as E:
                            time.sleep(2)
                            continue
                        break
                    os.remove(BASE_DIR + '/' + self.table_name + '_job.png')
                    os.remove(BASE_DIR + '/' + self.table_name + 'frame.png')
                    content = res['pic_str'].split('|')
                    loc_list = []
                    for i in content:
                        loc = i.split(',')
                        loc_list.append(loc)
                    action = ActionChains(driver)
                    for loca in loc_list:
                        action.move_to_element_with_offset(imgelement, int(loca[0]), int(loca[1])).click()
                        action.pause(1)
                    action.perform()
                    time.sleep(1)
                    wait.until(EC.presence_of_element_located((By.LINK_TEXT, '验 证'))).click()
                    time.sleep(1)
                    driver.refresh()
                    imgelement = driver.find_element_by_xpath('//*[@id="divValidateHtml"]/div')  # 定位验证码
                    driver.save_screenshot('d://aa.png')  # 截取当前网页，该网页有我们需要的验证码
                    location = imgelement.location  # 获取验证码x,y轴坐标
                    if location['x'] == 0:
                        # print('验证成功')
                        break
                    else:
                        # print('验证失败')
                        chaojiying.ReportError(res['pic_id'])
                    time.sleep(3)
                except:
                    # print('没有出现验证码')
                    break
            time.sleep(5)
            cookie = [item["name"] + "=" + item["value"] for item in driver.get_cookies()]
            cookiestr = '; '.join(item for item in cookie)
            print(cookiestr)
            driver.quit()
            return cookiestr
        else:
            return None
