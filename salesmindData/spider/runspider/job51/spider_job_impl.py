import random
from spider.runspider.job51.base_spider_job import BASEJOB
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from spider.models import *


class JOBAK(BASEJOB):
    """
    继承父类：BASEKJOB
    """
    def __init__(self, param):
        super(JOBAK, self).__init__(param)

    # 获取所有详情页 URL
    def parse_list(self):
        """
        解析列表页
        :return: 详情页url列表
        """
        if self.design_page:
            while self.page < self.design_page and self.sign == 0:
                button = self.wait.until(EC.presence_of_all_elements_located((By.XPATH, '//a[@title="下一页"]')))[0]
                if button.get_attribute('href'):
                    button.click()
                    self.page += 1
                    time.sleep(1)
                else:
                    break

        while True:
            print('{}抓取当前页码：{}'.format(self.table_name, self.page))
            url_list = []
            if self.sign == 0:
                self.check_yzm()  # 监测验证码
                try:
                    nodes = self.wait.until(
                        EC.presence_of_all_elements_located((By.XPATH, '//tr[contains(@id,"trBaseInfo")]')))
                except:
                    break
                for node in nodes:
                    try:
                        detail_url = node.find_element_by_xpath(
                            './td[@class="Common_list_table-id-text"]/span/a').get_attribute('href')
                        url_list.append(detail_url)
                    except:
                        continue
                SpiderData.objects.add_data_list(data_list=url_list, task_id=self.task_id)
                button = self.wait.until(EC.presence_of_all_elements_located((By.XPATH, '//a[@title="下一页"]')))[0]
                if button.get_attribute('href') and self.sign == 0:
                    time.sleep(3)
                    button.click()
                    self.page += 1
                else:
                    break
            else:
                break

    def run(self):
        """
        执行过程
        :return:
        """
        try:
            self.login()
            self.search_by_ak()
            self.parse_list()
            if self.sign == 0:
                SpiderTask.objects.finish_task1(task_id=self.task_id)
                print('{}已完成'.format(self.table_name))
            else:
                print('{}已中断'.format(self.table_name))
        except Exception as E:
            print(E)
            SpiderTask.objects.change_task1_status(task_id=self.task_id)
            print('{}已中断'.format(self.table_name))
        try:
            self.driver.get('https://ehire.51job.com/LoginOut.aspx')
            time.sleep(1)
        except:
            pass
        finally:
            self.driver.quit()
            self.update_data_count()


class JOBAKParse(JOBAK):
    """
    继承父类：JOBAK
    """
    def __init__(self, param):
        super(JOBAKParse, self).__init__(param=param)

    def parse_(self, url):
        """
        解析列表页，有条件的抓取详情页
        :param url: 详情url
        :return: 数据
        """
        self.driver.get(url)
        try:
            self.check_yzm()
        except:
            pass
        try:
            work_time = self.wait.until(
                EC.presence_of_all_elements_located((By.XPATH, '//td[text()="工作经验"]/../../tr[2]//td[@class="time"]')))[
                0].text
            sign = self.sel_by_method(work_time)
        except:
            sign = False
        return sign

    def parse_list(self):
        for data in self.get_data():
            url = data['data']
            if self.sign == 0:
                if self.contain_zhijin == 'on':
                    sign = self.parse_(url)
                else:
                    sign = True
                    self.driver.get(url)
                if sign:
                    item = self.parse_detail()
                else:
                    item = None
                if item:
                    self.col.insert_one(item)
                self.finish_list.append(data['id'])
                time.sleep(random.randint(3, 5))
            else:
                break

    def parse_detail_all(self):
        """
        解析详情页
        :return: 数据列表
        """
        item_list = []
        nodes = self.wait.until(EC.presence_of_all_elements_located((By.XPATH, '//td[text()="工作经验"]/../..//td[@class="tbb"]/table/tbody/tr')))
        for node in nodes:
            item = {}
            try:
                item['ID'] = \
                    self.wait.until(
                        EC.presence_of_element_located((By.XPATH, '//td[@class="name"]'))).text.strip().split(':')[
                        1]
            except:
                item['ID'] = ' '
            try:
                item['updatetime'] = self.wait.until(
                    EC.presence_of_element_located((By.XPATH, '//span[@id="lblResumeUpdateTime"]/b'))).text
            except:
                item['updatetime'] = ' '
            try:
                item['company_name'] = node.find_element_by_xpath('.//span[@class="bold"]').text
            except:
                item['company_name'] = ' '
            try:
                item['work_time'] = node.find_elements_by_xpath('.//td[@class="time"]')[
                    0].text
            except:
                item['work_time'] = ' '
            try:
                item['work_seniority'] = node.find_element_by_xpath('.//span[@class="gray"]').text.replace(' ', '')
            except:
                item['work_seniority'] = ' '
            try:
                item['position'] = node.find_element_by_xpath('.//strong').text
            except:
                item['position'] = ' '
            try:
                item['industry'] = self.wait.until(
                    EC.presence_of_element_located((By.XPATH, '//td[text()="行　业："]/../td[2]'))).text
            except:
                item['industry'] = ' '
            try:
                item['work_info'] = node.find_element_by_xpath('.//td[text()="工作描述："]/../td[2]').text.replace('\n', '')
            except:
                item['work_info'] = ' '
            try:
                item['scale'] = node.find_elements_by_xpath('.//td[@class="rtbox"]')[
                    0].text.split('|')[1]
            except:
                item['scale'] = ' '
            try:
                item['nature'] = node.find_elements_by_xpath('.//td[@class="rtbox"]')[
                    0].text.split('|')[2]
            except:
                item['nature'] = ' '
            item['date'] = int(time.time())
            item_list.append(item)
        return item_list

    def run(self):
        """
        执行过程
        :return:
        """
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


class JOBCK(BASEJOB):
    """
    继承父类：BASEJOB
    """
    def __init__(self, param):
        super(JOBCK, self).__init__(param=param)
        self.searching_company = ''

    def parse_(self, url):
        """
        解析列表页，有条件的抓取详情页
        :param url: 详情url
        :return: 数据
        """
        self.driver.get(url)
        self.check_yzm()
        work_time = self.wait.until(
            EC.presence_of_all_elements_located((
                By.XPATH, '//td[text()="工作经验"]/../../tr[2]//td[@class="time"]')))[0].text
        sign = self.sel_by_method(work_time)
        return sign

    def process(self):
        for data in self.get_data():
            company_query = data['data']
            if self.sign == 0:
                self.searching_company = company_query
                self.search_by_ck(company_query)
                url_list = self.parse_list()
                if len(url_list) == 0:
                    self.finish_list.append(data['id'])
                    continue
                js = 'window.open("https://www.baidu.com/");'
                self.driver.execute_script(js)
                handles = self.driver.window_handles
                for handle in handles:  # 切换窗口
                    if handle != self.driver.current_window_handle:
                        self.driver.switch_to.window(handle)
                for url in url_list:
                    if self.sign == 0:
                        if self.contain_zhijin == 'on':
                            sign = self.parse_(url)
                        else:
                            sign = True
                            self.driver.get(url)
                            time.sleep(1)
                        if sign:
                            item = self.parse_detail()
                        else:
                            item = None
                        if item:
                            item['输入公司名'] = company_query
                            self.col.insert_one(item)
                        time.sleep(random.randint(3, 5))
                    else:
                        break
                self.driver.close()
                self.driver.switch_to.window(handles[0])
                self.finish_list.append(data['id'])
            else:
                break

    def parse_list(self):
        """
        解析列表页
        :return: 详情页url列表
        """
        if self.design_page:
            while self.page < self.design_page:
                button = self.wait.until(EC.presence_of_element_located((By.ID, 'pagerBottomNew_nextButton')))
                if button.get_attribute('href') and self.sign == 0:
                    button.click()
                    self.page += 1
                    time.sleep(1)
                else:
                    break
        while True:
            url_list = []
            if self.sign == 0:
                self.check_yzm()  # 监测验证码
                try:
                    nodes = self.wait.until(
                        EC.presence_of_all_elements_located((By.XPATH, '//tr[contains(@id,"trBaseInfo")]')))
                except Exception:
                    break
                for node in nodes:
                    try:
                        detail_url = node.find_element_by_xpath(
                            './td[@class="Common_list_table-id-text"]/span/a').get_attribute('href')
                        url_list.append(detail_url)
                    except:
                        continue
                time.sleep(2)
                button = self.wait.until(EC.presence_of_all_elements_located((By.XPATH, '//a[@title="下一页"]')))[0]
                if button.get_attribute('href'):
                    button.click()
                    self.page += 1
                else:
                    break
            else:
                break
        return url_list

    def run(self):
        """
        执行过程
        :return:
        """
        try:
            self.login()
            if self.sign == 0:
                self.search_by_ak()
                self.process()
            if self.sign == 0:
                SpiderTask.objects.finish_task2(task_id=self.task_id)
                print("{}已完成".format(self.table_name))
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


class JOBID(BASEJOB):
    """
    继承父类：BASEJOB
    """

    def __init__(self, param):
        super(JOBID, self).__init__(param=param)

    def parse_list(self):
        self.check_yzm()
        try:
            url = self.driver.find_elements_by_xpath(
                '//tr[contains(@id,"trBaseInfo")]/td[@class="Common_list_table-id-text"]/span/a')[0].get_attribute('href')
        except:
            url = None
        return url

    def run(self):
        try:
            self.login()
            self.search_by_ak()
            for data in self.get_data():
                search_id = data['data']
                if self.sign == 0:
                    self.search_by_id(search_id)
                    url = self.parse_list()
                    if url:
                        js = 'window.open("https://www.baidu.com/");'
                        self.driver.execute_script(js)
                        handles = self.driver.window_handles
                        for handle in handles:  # 切换窗口
                            if handle != self.driver.current_window_handle:
                                self.driver.switch_to.window(handle)
                        self.driver.get(url)
                        item = self.parse_detail()
                        if item:
                            self.col.insert_one(item)
                        self.driver.close()
                        self.driver.switch_to.window(handles[0])
                    self.finish_list.append(data['id'])
                    time.sleep(random.randint(3, 5))
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
            self.driver.get('https://ehire.51job.com/LoginOut.aspx')
            time.sleep(1)
        except:
            pass
        finally:
            self.driver.quit()

