import random
from spider.models import *
import json
import requests
import time
from db.base_spider import BaseSpider
from spider.runspider.zhaopin.config import *


class ZhiLianDownByID(BaseSpider):
    def __init__(self, param):
        super(ZhiLianDownByID, self).__init__(param=param)
        self.type = param.get('type')
        self.headers = {
            'Cookie': param.get('login_cookie'),
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'
        }

    def get_access_token(self):
        # 获取access_token
        auth_url = 'http://ihr.zhaopin.com/api/user/authLogin.do'
        response = requests.get(url=auth_url, headers=self.headers)
        a = response.text
        a = json.loads(a)
        access_token = a['data']['token']
        return access_token

    def parse_list_id(self, ID):
        Data = {"start":0,"rows":30,"S_DISCLOSURE_LEVEL":2,"S_EXCLUSIVE_COMPANY":"上海门迪智能科技有限公司","S_RESUME_NUMBER":"GhQK0f1QUoyqsM2dJ95t1A","isrepeat":1,"sort":"complex"}
        Data['S_RESUME_NUMBER'] = ID
        url = 'https://rd5.zhaopin.com/api/custom/search/resumeListV2?_=1535611097164'
        r = requests.post(url, data=json.dumps(Data), headers=self.headers)
        data_dict = json.loads(r.content.decode())
        if data_dict['code'] != 0:
            print(data_dict)
            raise ValueError
        if len(data_dict['data']['dataList']) != 0:
            try:
                for node in data_dict['data']['dataList']:
                    url = 'https://rd5.zhaopin.com/api/rd/resume/detail?_=1535611494354&resumeNo={}_1_1%3B{}%3B{}'
                    url = url.format(node['id'], node['k'], node['t'])
                    r = requests.get(url,headers=self.headers)
                    content = json.loads(r.text)
                    item = {}
                    item['简历ID'] = content['data']['resumeNumber'].replace('_1_1','')
                    CurrentCareerStatus = content['data']['detail']['CurrentCareerStatus']
                    item['当前工作状态'] = WORKSTATUS[str(CurrentCareerStatus)]
                    try:
                        item['姓名'] = content['data']['candidate']['userName']
                    except:
                        item['姓名'] = ' '
                    try:
                        item['手机'] = content['data']['candidate']['mobilePhone']
                    except:
                        item['手机'] = ' '
                    try:
                        item['邮箱'] = content['data']['candidate']['email']
                    except:
                        item['邮箱'] = ' '
                    item['更新日期'] = content['data']['modifyDate']
                    starttime = content['data']['detail']['WorkExperience'][0]['DateStart'].split(' ')[0]
                    endttime = content['data']['detail']['WorkExperience'][0]['DateEnd'] if content['data']['detail']['WorkExperience'][0]['DateEnd'] else '至今'
                    item['工作时间'] = starttime + endttime
                    item['公司'] = content['data']['detail']['WorkExperience'][0]['CompanyName']
                    item['职位'] = content['data']['detail']['WorkExperience'][0]['JobTitle']
                    item['工作描述'] = content['data']['detail']['WorkExperience'][0]['WorkDescription'].replace('\r\n','')
                    item['date'] = int(time.time())
                    self.col.insert_one(item)
            except Exception as E:
                print(E)

    def parse_list_phone(self, phone):
        timeStamp = int(time.time())
        timeArray = time.localtime(timeStamp)
        otherStyleTime = time.strftime("%Y%m%d", timeArray)
        end = otherStyleTime[2:]
        start = str(int(otherStyleTime[2:]) - 10000)
        S_CreateDate = start + ',' + end
        Data = {"isNewList":False,"S_ResumeSource":2,"S_CreateDate":S_CreateDate,"S_HrId":"","ignoreStorage":1,"page":1,"pageSize":20,"S_Phone":""}
        Data['S_Phone'] = phone
        url = 'https://rd5.zhaopin.com/api/rd/resume/list?_=1535943959596'
        r = requests.post(url, data=json.dumps(Data), headers=self.headers)
        data_dict = json.loads(r.content.decode())
        if data_dict['code'] != 0:
            print(data_dict)
            raise ValueError
        if len(data_dict['data']['dataList']) != 0:
            try:
                for node in data_dict['data']['dataList']:
                    url = 'https://rd5.zhaopin.com/api/rd/resume/detail?_=1535946084495&resumeNo={}_1_1'
                    url = url.format(node['id'])
                    r = requests.get(url,headers=self.headers)
                    content = json.loads(r.text)
                    item = {}
                    item['简历ID'] = content['data']['resumeNumber'].replace('_1_1','')
                    CurrentCareerStatus = content['data']['detail']['CurrentCareerStatus']
                    item['当前工作状态'] = WORKSTATUS[str(CurrentCareerStatus)]
                    try:
                        item['姓名'] = content['data']['candidate']['userName']
                    except:
                        item['姓名'] = ' '
                    try:
                        item['手机'] = content['data']['candidate']['mobilePhone']
                    except:
                        item['手机'] = ' '
                    try:
                        item['邮箱'] = content['data']['candidate']['email']
                    except:
                        item['邮箱'] = ' '
                    timeStamp = content['data']['dateModified']
                    timeArray = time.localtime(timeStamp)
                    item['更新日期'] = time.strftime("%Y-%m-%d", timeArray)
                    starttime = content['data']['detail']['WorkExperience'][0]['DateStart'].split(' ')[0]
                    endttime = content['data']['detail']['WorkExperience'][0]['DateEnd'] if content['data']['detail']['WorkExperience'][0]['DateEnd'] else '至今'
                    item['工作时间'] = starttime + endttime
                    item['公司'] = content['data']['detail']['WorkExperience'][0]['CompanyName']
                    item['职位'] = content['data']['detail']['WorkExperience'][0]['JobTitle']
                    item['工作描述'] = content['data']['detail']['WorkExperience'][0]['WorkDescription'].replace('\r\n','')
                    item['date'] = int(time.time())
                    self.col.insert_one(item)
            except Exception as E:
                print(E)

    def run(self):
        try:
            for ID in self.get_data():
                if self.sign == 0:
                    if self.type == '0':
                        self.parse_list_id(ID['data'])
                    else:
                        self.parse_list_phone(ID['data'])
                    self.finish_list.append(ID['id'])
                    time.sleep(random.randint(5, 8))
                else:
                    break
            if self.sign == 0:
                SpiderTask.objects.finish_task2(self.task_id)
                print('{}爬取完成'.format(self.table_name))
            else:
                print('{}已中断'.format(self.table_name))
        except Exception as E:
            print(E)
            SpiderTask.objects.change_task2_status(self.task_id)
            print('{}已中断'.format(self.table_name))