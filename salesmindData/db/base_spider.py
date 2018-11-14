import copy
import random
import requests
from pymongo import MongoClient
from spider.models import *
from threading import Thread


class BaseSpider(object):

    def __init__(self, param):
        """
        :param param: 配置参数
        """
        # 任务ID
        self.task_id = param.get('task_id')
        # 下载文件名
        self.table_name = param.get('table_name')
        # 运行标志
        self.sign = 0
        # 已抓取参数列表
        self.finish_list = []
        # 连接数据库
        # client = MongoClient(host="139.196.29.181", port=27017)
        client = MongoClient(host="127.0.0.1", port=27017)
        db = client['salesmindSpider']
        # db.authenticate("spider1", "123456")
        self.col = db['Miindai_salesmind_' +self.table_name.split('-')[0] + '_' + str(self.task_id)]

    def get_proxy(self):
        """
        获取代理IP
        :return:
        """
        res = requests.get(
            'http://101.132.104.154:10000/get_proxy')
        content = res.content.decode()
        ipdict = json.loads(content)
        ip_list = ipdict.get('ip_list')
        ip_address = random.choice(ip_list)
        proxy = {
            'http': ip_address,
            'https': ip_address,
        }
        return proxy

    def get_data(self):
        """
        从数据库取出数据
        :return:
        """
        data_list = SpiderData.objects.get_data_list_by_task_id(self.task_id)
        return data_list

    def del_data(self):
        """
        标记删除url
        :param url:
        :return:
        """
        finish_list = copy.copy(self.finish_list)
        if finish_list:
            for data_id in finish_list:
                try:
                    SpiderData.objects.del_one_data(data_id=data_id)
                except:
                    pass
                self.finish_list.remove(data_id)

    def change_sign_status_1(self):
        while True:
            task = SpiderTask.objects.get_one_task(id=self.task_id)
            status = task.status_1
            if status != 1:
                self.sign = 1
                break
            time.sleep(5)

    def change_sign_status_2(self):
        while True:
            t = Thread(target=self.del_data)
            t.start()
            t.join()
            task = SpiderTask.objects.get_one_task(id=self.task_id)
            status = task.status_2
            if status != 1:
                self.sign = 1
                break
            time.sleep(5)
        self.del_data()

    def update_data_count(self):
        # 更新data数量
        count = SpiderData.objects.get_data_count_by_taskid(task_id=self.task_id)
        task = SpiderTask.objects.get_one_task(id=self.task_id)
        task.data_totle = count
        task.save()

    def cut_list(self, ls, n):
        if not isinstance(ls, list) or not isinstance(n, int):
            return []
        ls_len = len(ls)
        if n <= 0 or 0 == ls_len:
            return []
        if n >= ls_len:
            return [[i] for i in ls]
        else:
            j = ls_len // n
            ### j,j,j,...(前面有n-1个j),j+k
            # 步长j,次数n-1
            ls_return = []
            for i in range(0, (n - 1) * j, j):
                ls_return.append(ls[i:i + j])
            # 算上末尾的j+k
            ls_return.append(ls[(n - 1) * j:])
            return ls_return
