from threading import Thread

import requests
from spider.runspider.lagou.base_spider_lagou import BASELAGOU
from spider.models import *


class LAGOU(BASELAGOU):
    """
    继承父类：BASEZHAOPIN
    """
    def __init__(self, param):
        """
        初始化属性
        :param param:
        """
        super(LAGOU, self).__init__(param=param)
        self.base_url = param.get('base_url') + '.json'
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36',
            'Referer': param.get('base_url')
        }

    def parse_list(self):
        """
        解析列表页
        :param start_url:
        :return:
        """
        data = {
            'first': 'false',
            'sortField': '0',
            'havemark': '0'
        }
        pn = 1
        while True:
            if self.sign == 0:
                data['pn'] = pn
                while True:
                    try:
                        r = requests.post(self.base_url, headers=self.headers, data=data, timeout=5)
                        content = json.loads(r.text)
                        node_list = content['result']
                        if 'msg' in content:
                            continue
                        else:
                            break
                    except Exception:
                        continue
                url_list = []
                if node_list:
                    for node in node_list:
                        url = 'https://www.lagou.com/gongsi/{}.html'.format(node['companyId'])
                        url_list.append(url)
                    SpiderData.objects.add_data_list(data_list=url_list,task_id=self.task_id)
                    pn += 1
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
            self.parse_list()
            if self.sign == 0:
                SpiderTask.objects.finish_task1(task_id=self.task_id)
                print('{}已完成'.format(self.table_name))
            else:
                print("{}已中断".format(self.table_name))
        except Exception as E:
            print(E)
            SpiderTask.objects.change_task1_status(task_id=self.task_id)
            print('{}已中断'.format(self.table_name))
        self.update_data_count()


class LaGouParse(BASELAGOU):
    def __init__(self, param):
        super(LaGouParse, self).__init__(param=param)

    def parse(self, data_list):
        for data in data_list:
            url = data['data']
            if self.sign == 0:
                item = self.parse_detail(url)
                self.col.insert_one(item)
                self.finish_list.append(data['id'])
            else:
                break

    def run(self):
        try:
            l = self.get_data()
            cut_list = self.cut_list(l, 15)
            thread_list = []
            for data_list in cut_list:
                t = Thread(target=self.parse, args=(data_list,))
                t.start()
                thread_list.append(t)
            for t in thread_list:
                t.join()
            if self.sign == 0:
                SpiderTask.objects.finish_task2(task_id=self.task_id)
                print('{}已完成'.format(self.table_name))
            else:
                print("{}已中断".format(self.table_name))
        except Exception as E:
            print(E)
            SpiderTask.objects.change_task2_status(task_id=self.task_id)
            print('{}已中断'.format(self.table_name))


class LAGOU_COMPANY(BASELAGOU):
    """
    继承父类：BASEZHAOPIN
    """
    def __init__(self, param):
        """
        初始化属性
        :param table_name:
        :param company_list: list 公司列表
        """
        super(LAGOU_COMPANY, self).__init__(param=param)

    def parse_url(self, company):
        url = 'https://www.lagou.com/jobs/companyAjax.json?city=%E5%8C%97%E4%BA%AC&needAddtionalResult=false'
        data = {
            'first': 'true',
            'pn': '1',
            'kd': company
        }
        while True:
            try:
                proxy = self.get_proxy()
                a = requests.post(url, headers=self.headers, data=data, proxies=proxy, timeout=5)
                res = json.loads(a.content.decode())
                if res['msg'] and '您操作太频繁' in res['msg']:
                    continue
                break
            except:
                continue
        try:
            id = res['content']['result'][0]['companyId']
            detail = 'https://www.lagou.com/gongsi/' + str(id) + '.html'
        except:
            detail = None
        return detail

    def parse(self, data_list):
        for data in data_list:
            if self.sign == 0:
                url = self.parse_url(data['data'])
                # time.sleep(1)
                if url:
                    item = self.parse_detail(url)
                    item['query'] = data['data']
                    self.col.insert(item)
                self.finish_list.append(data['id'])
            else:
                break

    def run(self):
        """
        执行过程
        :return:
        """
        try:
            l = self.get_data()
            cut_list = self.cut_list(l, 15)
            thread_list = []
            for data_list in cut_list:
                t = Thread(target=self.parse, args=(data_list,))
                t.start()
                thread_list.append(t)
            for t in thread_list:
                t.join()
            if self.sign == 0:
                SpiderTask.objects.finish_task2(task_id=self.task_id)
                print('{}已完成'.format(self.table_name))
            else:
                print("{}已中断".format(self.table_name))
        except Exception as E:
            print(E)
            SpiderTask.objects.change_task2_status(task_id=self.task_id)
            print('{}已中断'.format(self.table_name))
