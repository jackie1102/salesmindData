import random
from spider.models import *
import urllib.parse
import requests
from spider.runspider.liepin.liepin_by_condition import LiePinConditionParse


class LiePinIdCompany(LiePinConditionParse):
    def __init__(self, param):
        super(LiePinIdCompany, self).__init__(param=param)
        self.param = param.get('param')
        self.type = param.get('type')

    def change_data(self):
        data_list = urllib.parse.unquote(self.param).replace('+', ' ').split('&')
        list1 = []
        list2 = []
        for i in data_list:
            list1.append(i.split('=')[0])
            list2.append(i.split('=')[1])
        data = dict(zip(list1, list2))
        return data

    def parse_list(self, Data):
        data = self.change_data()
        data['keys'] = Data
        data['curPage'] = 0
        while True:
            while True:
                try:
                    r = requests.post('https://lpt.liepin.com/cvsearch/search.json', data=data, headers=self.headers)
                    content = r.text
                    data_dict = json.loads(content)
                    if '异常' in data_dict.get('msg', ''):
                        self.login()
                        continue
                    break
                except:
                    continue
            for node in data_dict['data']['cvSearchResultForm']['cvSearchListFormList']:
                if 'http' not in node['resumeUrl']:
                    print(node['resumeUrl'])
                    url = 'https://lpt.liepin.com' + node['resumeUrl']
                else:
                    url = node['resumeUrl']
                if not self.all_work:
                    item = self.parse_detail(url, Data=Data)
                    if item:
                        self.col.insert(item)
                else:
                    self.parse_detail_all(url, Data=Data)
                time.sleep(random.randint(3, 5))
            if data['curPage']+1 < int(data_dict['data']['pageBarForm']['pageCount']) and self.sign == 0:
                data['curPage'] += 1
                time.sleep(random.randint(3, 5))
            else:
                break

    def parse_list2(self, Data):
        data = self.change_data()
        data['keys'] = Data
        data['curPage'] = 0
        while True:
            print('{}当前爬取页码：{}'.format(self.table_name, data['curPage']))
            while True:
                try:
                    r = requests.post('https://lpt.liepin.com/cvsearch/search.json', data=data, headers=self.headers)
                    content = r.text
                    data_dict = json.loads(content)
                    if '异常' in data_dict.get('msg', ''):
                        self.login()
                        continue
                    break
                except:
                    continue
            try:
                nodes = data_dict['data']['cvSearchResultForm']['cvSearchListFormList']
            except:
                nodes = []
            if len(nodes) != 0:
                for node in nodes:
                    item = {}
                    item['简历ID'] = node['resIdEncode']
                    txt = node['resContext'].replace('<font color="red">', '').replace('</font>', '')
                    try:
                        item['工作时间'] = txt.split('<')[0].split(' | ')[0]
                    except:
                        item['工作时间'] = '-'
                    try:
                        item['所在公司'] = txt.split('<')[0].split(' | ')[1]
                    except:
                        item['所在公司'] = '-'
                    try:
                        item['职位'] = txt.split('<')[0].split(' | ')[2]
                    except:
                        item['职位'] = '-'
                    try:
                        item['所在地区'] = node['resDqName']
                    except:
                        item['所在地区'] = '-'
                    item['更新时间'] = node['resModifytime']
                    item['date'] = int(time.time())
                    self.col.insert_one(item)
            if data['curPage'] < int(data_dict['data']['pageBarForm']['pageCount']) and self.sign == 0:
                data['curPage'] += 1
                time.sleep(random.randint(3, 5))
            else:
                break

    def run(self):
        try:
            for Data in self.get_data():
                if self.sign == 0:
                    if self.type:
                        self.parse_list2(Data=Data['data'])
                    else:
                        self.parse_list(Data=Data['data'])
                    self.finish_list.append(Data['id'])
                else:
                    break
                time.sleep(random.randint(3, 5))
            if self.sign == 0:
                SpiderTask.objects.finish_task2(task_id=self.task_id)
                print('{}完成'.format(self.table_name))
            else:
                print('{}中断'.format(self.table_name))
        except Exception as E:
            print(E)
            SpiderTask.objects.change_task2_status(task_id=self.task_id)
            print('{}中断'.format(self.table_name))

