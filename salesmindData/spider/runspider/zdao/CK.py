import json
import random
import time
from io import BytesIO
import requests
from PIL import Image
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

BORDER = 6
INIT_LEFT = 60


class CrackGeetest(object):
    def __init__(self):
        self.driver = webdriver.Chrome()
        self.wait = WebDriverWait(self.driver, 5)

    def get_geetest_button(self):
        """
        获取初始验证按钮
        :return:
        """
        button = self.wait.until(EC.element_to_be_clickable((By.XPATH, '//div[@class="gt_slider_knob gt_show"]')))
        return button
    
    def get_position(self):
        """
        获取验证码位置
        :return: 验证码位置元组
        """
        # self.driver.switch_to_alert()
        img = self.wait.until(EC.presence_of_element_located((By.XPATH, '//div[@class="gt_box"]')))
        # img = self.driver.find_element_by_xpath('//div[@class="geetest_canvas_img geetest_absolute"]')
        time.sleep(2)
        location = img.location
        size = img.size

        top, bottom, left, right = location['y'], location['y'] + size['height'], location['x'], location['x'] + size[
            'width']
        return (top, bottom, left, right)
    
    def get_screenshot(self):
        """
        获取网页截图
        :return: 截图对象
        """
        screenshot = self.driver.get_screenshot_as_png()
        screenshot = Image.open(BytesIO(screenshot))
        return screenshot
    
    def get_slider(self):
        """
        获取滑块
        :return: 滑块对象
        """
        slider = self.driver.find_element_by_xpath('//div[@class="gt_slider_knob gt_show"]')
        return slider
    
    def get_geetest_image(self, name='captcha.png'):
        """
        获取验证码图片
        :return: 图片对象
        """
        top, bottom, left, right = self.get_position()
        print('验证码位置', top, bottom, left, right)
        screenshot = self.get_screenshot()
        captcha = screenshot.crop((left, top, right, bottom))
        captcha.save(name)
        return captcha

    def get_gap(self, image1, image2):
        """
        获取缺口偏移量
        :param image1: 不带缺口图片
        :param image2: 带缺口图片
        :return:
        """
        # left = 60
        left = 80
        print(image1.size)
        for i in range(left, image1.size[0]):
            for j in range(image1.size[1]):
                if not self.is_pixel_equal(image1, image2, i, j):
                    left = i
                    return left
        return left
    
    def is_pixel_equal(self, image1, image2, x, y):
        """
        判断两个像素是否相同
        :param image1: 图片1
        :param image2: 图片2
        :param x: 位置x
        :param y: 位置y
        :return: 像素是否相同
        """
        # 取两个图片的像素点
        pixel1 = image1.load()[x, y]
        pixel2 = image2.load()[x, y]
        threshold = 60
        if abs(pixel1[0] - pixel2[0]) < threshold and abs(pixel1[1] - pixel2[1]) < threshold and abs(
                pixel1[2] - pixel2[2]) < threshold:
            return True
        else:
            return False
    
    def get_track(self, distance):
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
        mid = distance * 3 / 5
        # 计算间隔
        t = 0.2
        # 初速度
        v = 0
        
        while current < distance:
            if current < mid:
                # 加速度为正2
                a = random.randint(2, 6)
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
    
    def move_to_gap(self, slider, track):
        """
        拖动滑块到缺口处
        :param slider: 滑块
        :param track: 轨迹
        :return:
        """
        ActionChains(self.driver).click_and_hold(slider).perform()
        for x in track:
            ActionChains(self.driver).move_by_offset(xoffset=x, yoffset=0).perform()
        time.sleep(1)
        ActionChains(self.driver).release().perform()
    
    def login(self):
        """
        登录
        :return: None
        """
        submit = self.wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'login-btn')))
        submit.click()
        time.sleep(10)
        print('登录成功')
    
    def crack(self):
        while True:
            try:
                # 输入用户名密码
                # self.open()
                # 点击验证按钮
                # button = self.get_geetest_button()
                # button.click()
                # 获取验证码图片
                image1 = self.get_geetest_image('captcha1.png')
                # 点按呼出缺口
                slider = self.get_slider()
                slider.click()
                time.sleep(2)
                # 获取带缺口的验证码图片
                image2 = self.get_geetest_image('captcha2.png')
                # 获取缺口位置
                gap = self.get_gap(image1, image2)
                print('缺口位置', gap)
                # 减去缺口位移
                gap -= BORDER
                # 获取移动轨迹
                track = self.get_track(gap)
                print('滑动轨迹', track)
                # 拖动滑块
                self.move_to_gap(slider, track)
                time.sleep(3)
                self.driver.refresh()
                time.sleep(3)
            except Exception as E:
                print(E)
                break


if __name__ == '__main__':
    crack = CrackGeetest()
    crack.crack()
