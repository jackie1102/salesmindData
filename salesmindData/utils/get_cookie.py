import time
from selenium import webdriver


def get_cookie(url):
    # 打开浏览器
    driver = webdriver.Chrome()
    # 请求起始url
    driver.get(url)
    time.sleep(30)
    cookies = driver.get_cookies()
    driver.quit()
    # 打印cookie
    return cookies
