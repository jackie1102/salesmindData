import random

import requests
from spider.models import *
from spider.runspider.zhaopin_.base_zhaopin import BaseZhaoPin


class ZhaoPin(BaseZhaoPin):
    """
    连接数据库
    """
    def __init__(self, param):
        """
        初始化属性
        """
        super(ZhaoPin, self).__init__(param=param)
        self.status = param.get('status')
        self.payload = json.loads(param.get('param'))
        self.start_page = int(param.get('start_page')) if param.get('start_page') else 1
        self.access_token = ''

    def parse_list(self, nodes):
        """
        解析列表页，储存url
        :param nodes:
        :return:
        """
        detail_list = []
        for node in nodes:
            if self.sign == 0:
                if self.status == 'on' and node['careerStatus'] == '在职':
                    modifyDate = node['modifyDate']
                    url = 'http://ihr.zhaopin.com/resumesearch/getresumedetial.do?access_token={}&resumeNo={}_1_1&searchresume=1&resumeSource=1&t={}&k={}'
                    url = url.format(self.access_token, node['id'], node['t'], node['k'])
                    detail_url = url
                    detail_list.append(detail_url+';;' + modifyDate)
                if not self.status:
                    modifyDate = node['modifyDate']
                    url = 'http://ihr.zhaopin.com/resumesearch/getresumedetial.do?access_token={}&resumeNo={}_1_1&searchresume=1&resumeSource=1&t={}&k={}'
                    url = url.format(self.access_token, node['id'], node['t'], node['k'])
                    detail_url = url
                    detail_list.append(detail_url + ';;' + modifyDate)
            else:
                break
        return detail_list

    def run(self):
        """
        执行
        :return:
        """
        try:
            try:
                self.access_token = self.get_access_token()
            except Exception as E:
                print(E)
                SpiderTask.objects.change_task1_status(task_id=self.task_id)
            while True:
                self.payload['start'] = int(self.start_page) - 1
                print("{}当前抓取页码为：{}".format(self.table_name,self.start_page))
                while True:
                    try:
                        r = requests.post('https://rdapi.zhaopin.com/rd/search/resumeList',
                                          headers=self.headers, data=json.dumps(self.payload), timeout=3)
                        break
                    except:
                        continue
                data_dict = json.loads(r.content.decode())
                node_list = data_dict['data']['dataList']
                if len(node_list) != 0 and self.sign == 0:
                    data_list = self.parse_list(node_list)
                    SpiderData.objects.add_data_list(data_list=data_list, task_id=self.task_id)
                    if self.start_page < 134 and self.sign == 0:
                        self.start_page += 1
                        time.sleep(3)
                    else:
                        break
                else:
                    break
            if self.sign == 0:
                SpiderTask.objects.finish_task1(task_id=self.task_id)
                print('爬虫：{}  抓取完成'.format(self.table_name))
            else:
                user = ZhiLianId.objects.get_one_ID_by_id(self.username_id)
                user.status = 0
                user.task_id = 0
                user.save()
                print('爬虫：{}  抓取中断'.format(self.table_name))
        except Exception as E:
            print(E)
            user = ZhiLianId.objects.get_one_ID_by_id(self.username_id)
            user.status = 0
            user.task_id = 0
            user.save()
            SpiderTask.objects.change_task1_status(task_id=self.task_id)
            print('爬虫：{}  抓取中断'.format(self.table_name))
        self.update_data_count()







