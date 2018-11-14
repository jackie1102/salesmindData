import random
import requests
from spider.runspider.zhaopin.config import *
from spider.runspider.zhaopin.zhaopin_condition import ZhaoPin
from spider.models import *


class ZhaoPinParse(ZhaoPin):
    def __init__(self, param):
        # 连接数据库
        super(ZhaoPinParse, self).__init__(param=param)

    def get_detail(self, data):
        """
        解析详情，并标记删除url
        :param sql_data:
        :return:
        """
        sql_data = data['data']
        url = sql_data.split(';;')[0]
        r = requests.get(url, headers=self.headers)
        try:
            data_dict = json.loads(r.content.decode())
        except Exception as E:
            return
        if '异常' in data_dict.get('message', ''):
            # print(data_dict)
            raise ValueError
        if '重新登录' in data_dict.get('message', ''):
            # print(data_dict)
            raise ValueError
        try:
            Data = {}
            Data['modifyDate'] = sql_data.split(';;')[1]
            Data['data'] = data_dict['data']
            Data['detail'] = json.loads(data_dict['data']['detialJSonStr'])
            self.parse_detail(Data)
        except Exception as E:
            print(E)
            pass
        self.finish_list.append(data['id'])

    def parse_detail(self, data):
        """
        提取数据
        :param data:
        :return:
        """
        item = {}
        item['姓名'] = data['data']['userDetials']['userName']
        item['人才类型'] = data['detail'].get('tags')
        item['年龄'] = data['data']['userDetials']['birthYear']
        gender = data['data']['userDetials']['gender']
        if gender == '1':
            item['性别'] = '男'
        elif gender == '2':
            item['性别'] = '女'
        province = AREA.get(data['data']['userDetials']['provinceStateId']) if AREA.get(data['data']['userDetials']['provinceStateId']) else ''
        city = AREA.get(data['data']['userDetials']['cityId']) if AREA.get(data['data']['userDetials']['cityId']) else '-'
        item['现居住地'] = province + '-' + city
        item['简历id'] = data['data']['resumeNo']
        try:
            item['工作状态'] = WORKSTATUS.get(data['detail']['DesiredPosition'][0]['CurrentCareerStatus'])
        except:
            item['工作状态'] = '无'
        start_time = data['detail']['WorkExperience'][0]['DateStart'].split(' ')[0] + '-'
        end_time = data['detail']['WorkExperience'][0]['DateEnd'] if data['detail']['WorkExperience'][0]['DateEnd'] != '' else '至今'
        item['工作时间'] = start_time + end_time
        Salary = data['detail']['WorkExperience'][0].get('Salary')
        if Salary:
            item['工作薪资'] = str(int(Salary[:len(Salary )//2].replace(Salary[:len(Salary)//2][-1], '0'))) + '-' + str(int(Salary[len(Salary)//2:]))
        else:
            item['工作薪资'] = '-'
        item['公司名称'] = data['detail']['WorkExperience'][0].get('CompanyName')
        item['公司行业'] = INDUSTRY.get(data['detail']['WorkExperience'][0]['CompanyIndustry']) if data['detail']['WorkExperience'][0].get('CompanyIndustry') else '-'
        item['企业性质'] = NATURE.get(data['detail']['WorkExperience'][0]['CompanyProperty']) if data['detail']['WorkExperience'][0].get('CompanyProperty') else '-'
        item['公司规模'] = SIZE.get(data['detail']['WorkExperience'][0]['CompanySize']) if data['detail']['WorkExperience'][0].get('CompanySize') else '-'
        item['工作职位'] = data['detail']['WorkExperience'][0].get('JobTitle')
        item['工作描述'] = data['detail']['WorkExperience'][0].get('WorkDescription').replace('\r\n', '') if data['detail']['WorkExperience'][0].get('WorkDescription') else '-'
        item['更新时间'] = data['modifyDate']
        item['date'] = int(time.time())
        # print(item)
        self.col.insert(item)

    def run(self):
        """
        执行
        :return:
        """
        try:
            data_list = self.get_data()
            for data in data_list:
                if self.sign == 0:
                    self.get_detail(data)
                    time.sleep(random.randint(3, 5))
                else:
                    break
            if self.sign == 0:
                SpiderTask.objects.finish_task2(task_id=self.task_id)
                print('爬虫{}抓取完成'.format(self.table_name))
            else:
                print('{}已中断'.format(self.table_name))
        except Exception as E:
            print(str(E))
            SpiderTask.objects.change_task2_status(task_id=self.task_id)
            print('{}已中断'.format(self.table_name))




