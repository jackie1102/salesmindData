import re
from pymongo import *
import time
from selenium import webdriver

from salesmindData.settings import pool
from utils.update import update_task_state


class MyException(Exception):
    def __init__(self, message):
        Exception.__init__(self)
        self.message = message


class EMAIL(object):

    def __init__(self, param):
        self.table_name = param.get('table_name')
        self.data_list = param.get('data_list')
        client = MongoClient(host="139.196.29.181", port=27017)
        db = client['salesmindSpider']
        db.authenticate("spider1", "123456")
        self.col = db[self.table_name]
        self.user_id = param.get('user_id')
        self.sign = 0

    def change_sign(self):
        cnn = pool.connection()
        cursor = cnn.cursor()
        while True:
            cursor.execute('select state from python_task where table_name="{}" and user_id="{}"'.format(self.table_name,self.user_id))
            state = cursor.fetchone()[0]
            if state != 1:
                self.sign = 1
                cursor.close()
                cnn.close()
                break
            time.sleep(5)

    def run(self):
        for line in self.data_list:
            if self.sign == 0:
                driver = webdriver.Chrome()
                driver.implicitly_wait(10)
                try:
                    print(line)
                    name = line[0]
                    url = line[1]
                    keyword_list = ['我们', '联系', '招贤纳士', '关于', '加入']
                    for num in range(2):
                        try:
                            driver.get(url)
                            time.sleep(1)
                        except:
                            continue
                        break
                    print(url)
                    content = driver.page_source
                    # print content
                    email_list = re.findall(r'>.*?([a-zA-Z0-9_-]+@[a-zA-Z0-9_-]+[\.a-zA-Z0-9_-]+?)<', content, re.S)
                    if len(email_list) == 0:
                        # print('11111')
                        email_list = re.findall(r'<a href=".*?([a-zA-Z0-9_-]+@[a-zA-Z0-9_-]+[\.a-zA-Z0-9_-]+?)">', content, re.S)
                        # print(len(email_list))
                        if len(email_list) == 0:
                            # print('88')
                            for num in range(2):
                                for keyword in keyword_list:
                                    for num in range(2):
                                        try:
                                            driver.get(url)
                                            time.sleep(2)
                                        except:
                                            continue
                                        break
                                    # print('11')
                                    try:
                                        email_url = driver.find_element_by_partial_link_text(keyword).get_attribute('href')
                                        for num in range(2):
                                            try:
                                                driver.get(email_url)
                                                time.sleep(1)
                                            except:
                                                continue
                                            break
                                        content = driver.page_source
                                        # print content
                                        email_list = re.findall(r'>.*?([a-zA-Z0-9_-]+@[a-zA-Z0-9_-]+[\.a-zA-Z0-9_-]+?)<', content, re.S)
                                        if len(email_list) == 0:
                                            email_list = re.findall(r'<a href=".*?([a-zA-Z0-9_-]+@[a-zA-Z0-9_-]+[\.a-zA-Z0-9_-]+?)">', content, re.S)
                                            if len(email_list) == 0:
                                                for keyword in keyword_list:
                                                    try:
                                                        email_url = driver.find_element_by_partial_link_text(keyword).get_attribute('href')
                                                        for num in range(3):
                                                            try:
                                                                driver.get(email_url)
                                                                time.sleep(1)
                                                            except:
                                                                continue
                                                            break

                                                        content = driver.page_source
                                                        # print content
                                                        email_list = re.findall(
                                                            r'>.*?([a-zA-Z0-9_-]+@[a-zA-Z0-9_-]+[\.a-zA-Z0-9_-]+?)<', content, re.S)
                                                        if len(email_list) == 0:
                                                            email_list = re.findall(
                                                                r'<a href=".*?([a-zA-Z0-9_-]+@[a-zA-Z0-9_-]+[\.a-zA-Z0-9_-]+?)">',
                                                                content, re.S)
                                                            if len(email_list) == 0:
                                                                raise MyException('Email Not Found ')
                                                    except:
                                                        continue
                                                    break
                                    except Exception as e:
                                        # print(e)
                                        continue
                                    break
                                if len(email_list) == 0:
                                    continue
                                else:
                                    break
                except:
                    driver.quit()
                    continue

                Email_list = []
                for email in email_list:
                    if '>' in email:
                        email = email.split('>')[1]
                    Email_list.append(email)
                Email_list = list(set(Email_list))
                email = ';'.join(Email_list)
                item = {}
                item['name'] = name
                item['email'] = email
                print(item)
                if item['email'] != '':
                    self.col.insert_one(item)
                driver.quit()
            else:
                break
        if self.sign == 0:
            self.update_task()

    def update_task(self):
        """
        更新任务状态
        :return:
        """
        update_task_state(self.table_name)
        print('{}爬取完成'.format(self.table_name))