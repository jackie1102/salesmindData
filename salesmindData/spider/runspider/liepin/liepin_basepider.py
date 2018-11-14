import os
import random
import time

from selenium.webdriver.chrome.options import Options

from utils.chaojiying import Chaojiying_Client
from db.base_spider import BaseSpider
from PIL import Image
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from spider.models import *
from salesmindData.settings import BASE_DIR


class LiePinBaseSpider(BaseSpider):

    def __init__(self, param):
        super(LiePinBaseSpider, self).__init__(param)
        self.username = param.get('username')
        self.password = param.get('password')
        self.headers = {}
        self.login()

    def login(self):
        chrome_options = Options()
        chrome_options.add_argument('window-size=1920x2000')  # 指定浏览器分辨率
        chrome_options.add_argument('--disable-gpu')  # 谷歌文档提到需要加上这个属性来规避bug
        chrome_options.add_argument('--hide-scrollbars')  # 隐藏滚动条, 应对一些特殊页面
        chrome_options.add_argument('--headless')  # 浏览器不提供可视化页面. linux下如果系统不支持可视化不加这条会启动失败
        # brower = webdriver.Chrome(chrome_options=chrome_options)
        brower = webdriver.Chrome()
        brower.maximize_window()
        wait = WebDriverWait(brower, 10)
        brower.get('https://passport.liepin.com/e/account')
        url1 = brower.current_url
        while True:
            yz_error = False
            newpassword = None
            if self.sign == 0:
                wait.until(EC.presence_of_element_located(
                    (By.XPATH, '//*[@id="user-reglpt"]/div[1]/div[2]/div/div[1]/ul/li[2]'))).click()
                user = wait.until(EC.presence_of_element_located((
                    By.XPATH, '//section[@data-selector="PC"]//input[@name="user_login"]')))
                user.clear()
                for item in self.username:
                    user.send_keys(item)
                    time.sleep(random.uniform(0.3, 0.6))
                time.sleep(1)
                pwd = wait.until(EC.presence_of_element_located((
                        By.XPATH, '//section[@data-selector="PC"]//input[@name="user_pwd"]')))
                pwd.clear()
                for item in self.password:
                    pwd.send_keys(item)
                    time.sleep(random.uniform(0.3, 0.6))
                time.sleep(1)
                wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="verify-button"]'))).click()
                while True:
                    if self.sign == 0:
                        imgelement = brower.find_element_by_xpath('//*[@id="captcha"]/iframe')  # 定位验证码
                        location = imgelement.location  # 获取验证码x,y轴坐标
                        if location['x'] == 0:
                            return
                        brower.save_screenshot('liepin.png')  # 截取当前网页，该网页有我们需要的验证码
                        size = imgelement.size  # 获取验证码的长宽
                        rangle = (int(location['x']), int(location['y']), int(location['x'] + size['width']),
                                  int(location['y'] + size['height']))  # 写成我们需要截取的位置坐标
                        i = Image.open('liepin.png')  # 打开截图
                        frame = i.crop(rangle)  # 使用Image的crop函数，从截图中再次截取我们需要的区域
                        frame.save('liepinframe.png')
                        chaojiying = Chaojiying_Client('jackie1102', 'salesmind1800', '9004')
                        im = open('liepinframe.png', 'rb').read()
                        while True:
                            try:
                                res = chaojiying.PostPic(im, 9004)
                            except Exception as E:
                                time.sleep(2)
                                continue
                            break
                        os.remove('liepin.png')
                        os.remove('liepinframe.png')
                        content = res['pic_str'].split('|')
                        loc_list = []
                        for i in content:
                            loc = i.split(',')
                            loc_list.append(loc)
                        action = ActionChains(brower)
                        for loca in loc_list:
                            action.move_to_element_with_offset(imgelement, int(loca[0]), int(loca[1])).click()
                        action.move_to_element_with_offset(imgelement, 210, 245).click()
                        action.perform()
                        time.sleep(5)
                        url2 = brower.current_url
                        for i in range(2):
                            if url1 != url2:
                                try:
                                    node = brower.find_element_by_xpath('//h1[text()="账号登录异常"]')
                                    if node:
                                        newpassword = self.change_pwd(brower, wait)
                                        brower.find_element_by_xpath('//*[text()="立即登录"]').click()
                                        break
                                except:
                                    break
                            else:
                                time.sleep(3)
                        else:
                            yz_error = True
                        break
                    else:
                        break
                if yz_error:
                    continue
                if newpassword:
                    self.password = newpassword
                    task = SpiderTask.objects.get_one_task(id=self.task_id)
                    data = json.loads(task.param)
                    data["password"] = newpassword
                    task.param = json.dumps(data)
                    task.save()
                    continue
                cookie = [item["name"] + "=" + item["value"] for item in brower.get_cookies()]
                cookiestr = '; '.join(item for item in cookie)
                print(cookiestr)
                self.headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36',
                    'Cookie': cookiestr,
                    'X-Requested-With': 'XMLHttpRequest',
                    'Referer': 'https://lpt.liepin.com/cvsearch/showcondition/',
                    'Host': 'lpt.liepin.com',
                    'Origin': 'https://lpt.liepin.com'
                }
                brower.quit()
                break
            else:
                break

    def change_pwd(self, brower, wait):
        brower.find_element_by_xpath('//a[text()="修改密码"]').click()
        wait.until(EC.presence_of_element_located((By.XPATH, '//input[@name="oldpwd"]'))).send_keys(self.password)
        if self.password == 'salesmind1800':
            newpassword = 'salesmind18'
        else:
            newpassword = 'salesmind1800'
        wait.until(EC.presence_of_element_located((By.XPATH, '//input[@name="user_pwd"]'))).send_keys(newpassword)
        wait.until(EC.presence_of_element_located((By.XPATH, '//input[@data-nick="ok_new_password"]'))).send_keys(
            newpassword)
        while True:
            imgelement = wait.until(
                EC.presence_of_element_located((By.XPATH, '//img[@data-selector="ver-code"]')))
            location = imgelement.location  # 获取滑条x,y轴坐标
            if location['x'] == 0:
                return
            brower.save_screenshot(BASE_DIR + '/' + 'liepin_.png')  # 截取当前网页，该网页有我们需要的验证码
            size = imgelement.size  # 获取滑条的长宽
            rangle = (int(location['x']), int(location['y']), int(location['x'] + size['width']),
                      int(location['y'] + size['height']))  # 写成我们需要截取的位置坐标
            i = Image.open(BASE_DIR + '/' + "liepin_.png")  # 打开截图
            frame4 = i.crop(rangle)  # 使用Image的crop函数，从截图中再次截取我们需要的区域
            frame4.save(BASE_DIR + '/' + 'liepinyzm.png')
            chaojiying = Chaojiying_Client('jackie1102', 'salesmind1800', '1902')
            im = open(BASE_DIR + '/' + 'liepinyzm.png', 'rb').read()
            res = chaojiying.PostPic(im, 1902)
            pic_str = res['pic_str']
            os.remove(BASE_DIR + '/' + "liepin_.png")
            os.remove(BASE_DIR + '/' + "liepinyzm.png")
            inpt = brower.find_element_by_xpath('//input[@name="verifycode"]')
            inpt.clear()
            time.sleep(1)
            inpt.send_keys(pic_str)
            time.sleep(1)
            brower.find_element_by_xpath('//button[@type="submit"]').click()
            time.sleep(1)
            try:
                button = brower.find_element_by_xpath('//a[@data-name="ok"]')
                if button:
                    chaojiying.ReportError(res['pic_id'])
                    button.click()
                    time.sleep(2)
                    imgelement.click()
            except:
                break
        time.sleep(1)
        return newpassword


if __name__ == '__main__':
    S = LiePinBaseSpider({})
    S.login()
