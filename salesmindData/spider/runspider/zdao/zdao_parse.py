import json
import time
from lxml import etree
import requests
from pymongo import MongoClient
from spider.runspider.zdao.conf import *
from spider.runspider.zdao.CK import CrackGeetest
from salesmindData.settings import pool
from utils.update import update_task_state


# 连接数据库
client = MongoClient(host="139.196.29.181", port=27017)
db = client['salesmindSpider']
db.authenticate("spider1", "123456")
col = db[TABLE_NAME]
headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36',
            'Host': 'www.zdao.com',
            'X-Requested-With': 'XMLHttpRequest',
            'Origin': 'https://www.zdao.com',
            'Cookie': ''
        }


def get_url():
    """
    从数据库取出url
    :return:
    """
    cnn = pool.connection()
    cursor = cnn.cursor()
    cursor.execute('select detail_url from zdao_spider_url where table_name="{}" and user_id="{}" and isdel=0;'.format(TABLE_NAME, USER_ID))
    url_list = cursor.fetchall()
    print(url_list)
    cursor.close()
    cnn.close()
    return url_list


def del_url(url):
    """
    标记删除url
    :param url:
    :return:
    """
    cnn = pool.connection()
    cursor = cnn.cursor()
    cursor.execute(
        'update zdao_spider_url set isdel=1 WHERE table_name="{}" AND user_id="{}" and detail_url="{}";'.format(TABLE_NAME, USER_ID, url))
    cursor.close()
    cnn.close()

def check_YZM():
    YZ = CrackGeetest()
    YZ.driver.get('https://www.zdao.com/user/login')
    time.sleep(2)
    YZ.crack()
    YZ.driver.find_element_by_xpath('//div[@class="normal_tab tab_account"]').click()
    YZ.driver.find_element_by_xpath('//div[@class="login_by_account"]/div[1]/input').send_keys('13816370036')
    time.sleep(0.5)
    YZ.driver.find_element_by_xpath('//div[@class="login_by_account"]/div[2]/input').send_keys('salesmind18')
    time.sleep(0.5)
    YZ.driver.find_element_by_xpath('//div[@class="login_by_account"]/div[4]').click()
    # 设置等待时间输入关键字 点击搜索
    time.sleep(1)
    YZ.driver.get('https://www.zdao.com/site/searchperson?keywords=总经理')
    time.sleep(2)
    YZ.crack()
    cookie = [item["name"] + "=" + item["value"] for item in YZ.driver.get_cookies()]
    cookiestr = ';'.join(item for item in cookie)
    global headers
    headers['Cookie'] = cookiestr
    YZ.driver.quit()
        

def get_detail(url):
    """
    解析详情页
    :return: dic  item:采集数据
    """
    while True:
        while True:
            try:
                r = requests.get(url, headers=headers, timeout=5)
                content = r.content.decode()
                break
            except:
                continue
        try:
            code = json.loads(content)['errno']
            if code != 0:
                print(json.loads(content))
                try:
                    check_YZM()
                except:
                    pass
        except:
            break
    html = etree.HTML(r.content.decode())
    item = {}
    name = html.xpath('//p[@class="user_name"]/text()')
    item['姓名'] = name[0] if len(name) > 0 else ' '
    position = html.xpath('//p[@class="user_title"]/text()')
    item['职位'] = position[0] if len(position) > 0 else ' '
    company = html.xpath('//div[@class="user_career"]/a/text()')
    item['公司'] = company[0] if len(company) > 0 else ' '
    slogan = html.xpath('//p[@class="business"]/text()')
    item['slogan'] = slogan[0].strip() if len(slogan) > 0 else ' '
    company_name = html.xpath(
        '//div[@class="content_main company_container"]//div[@class="small_title"]/text()')
    item['公司名'] = company_name[0].strip() if len(company_name) > 0 else ' '
    time = html.xpath('//div[@class="content_main company_container"]//div[@class="half_item_info"][1]/text()')
    item['成立时间'] = time[0].split('：')[1].replace('注册资本', '').strip() if len(time) > 0 else ' '
    try:
        item['注册资本'] = \
            html.xpath('//div[@class="content_main company_container"]//div[@class="half_item_info"][1]/text()')[
                0].split('：')[-1].strip()
    except:
        item['注册资本'] = ' '
    try:
        try:
            school = html.xpath(
                '//div[@class="content_main ib experience"]/div[2]//div[@class="name"]/text()')[0]
        except:
            school = ''
        try:
            major = html.xpath(
                '//div[@class="content_main ib experience"]/div[2]//div[@class="half_item_info major"]/text()')[
                0]
        except:
            major = ''
        try:
            time = html.xpath(
                '//div[@class="content_main ib experience"]/div[2]//div[@class="half_item_info education_time"]/text()')[
                0]
        except:
            time = ''

        item['教育经历'] = school + '>' + major + '>' + time
    except:
        item['教育经历'] = ' '
    try:
        item['邮箱'] = html.xpath('//a[contains(@class,"mail_item")]/text()')[0].strip()
    except:
        item['邮箱'] = ' '
    try:
        item['QQ'] = html.xpath('//div[contains(@class,"QQ_item")]/text()')[0].strip()
    except:
        item['QQ'] = ' '
    try:
        item['微信'] = html.xpath('//div[contains(@class,"weixin_item")]/text()')[0].strip()
    except:
        item['微信'] = ' '
    try:
        item['手机'] = html.xpath('//a[contains(@class,"mobile_item")]/text()')[0].strip()
    except:
        item['手机'] = ' '
    try:
        item['性别'] = html.xpath('//div[contains(@class,"gender")]/text()')[0]
    except:
        item['性别'] = ' '
    try:
        item['所属行业'] = html.xpath('//div[contains(@class,"industry_name")]/text()')[0]
    except:
        item['所属行业'] = ' '
    try:
        item['所在地区'] = html.xpath('//div[@class="item_info town_code"]/text()')[0]
    except:
        item['所在地区'] = ' '
    try:
        item['家乡'] = html.xpath('//div[@class="item_info hometown_code"]/text()')[0]
    except:
        item['家乡'] = ' '
    print(item)
    return item


def parse_detail():
    check_YZM()
    url_list = get_url()
    for url in url_list:
        item = get_detail(url[0])
        col.insert(item)
        del_url(url[0])
    update_task_state(TABLE_NAME)
    print('{}爬取完成'.format(TABLE_NAME))


if __name__ == '__main__':
    parse_detail()