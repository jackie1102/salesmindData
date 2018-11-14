import random
import requests
from spider.runspider.zhaopin.config import *
from spider.models import *
from spider.runspider.zhaopin.base_zhaopin import BaseZhaoPin


class ZhaoPin_Company(BaseZhaoPin):
    def __init__(self, param):
        super(ZhaoPin_Company, self).__init__(param=param)
        self.data = json.loads(param.get('param'))
        self.last = param.get("last")
        try:
            self.access_token = self.get_access_token()
        except Exception as E:
            print(E)
            SpiderTask.objects.change_task2_status(task_id=self.task_id)

    def generator_data(self):
        for data in self.get_data():
            # print(company)
            company = data['data']
            if self.last:
                self.data['S_COMPANY_NAME_LAST'] = company
            else:
                self.data['S_COMPANY_NAME_ALL'] = company
            yield self.data, data

    def parse_list(self, Data, company):
        while True:
            # print('当前页码：{}'.format(int(Data['start'])))
            url = 'https://rdapi.zhaopin.com/rd/search/resumeListV2'
            r = requests.post(url, data=json.dumps(Data), headers=self.headers)
            try:
                data_dict = json.loads(r.content.decode())
            except Exception as E:
                return
            if '失败' in data_dict.get('message', ''):
                # print(data_dict)
                return
            if data_dict['code'] != 0:
                # print(data_dict)
                raise ValueError
            if len(data_dict['data']['dataList']) != 0:
                try:
                    for node in data_dict['data']['dataList']:
                        if self.sign == 0:
                            data = {}
                            data['modifyDate'] = node['modifyDate']
                            data['state'] = node['careerStatus']
                            url = 'http://ihr.zhaopin.com/resumesearch/getresumedetial.do?access_token={}&resumeNo={}_1_1&searchresume=1&resumeSource=1&t={}&k={}'
                            url = url.format(self.access_token, node['id'], node['t'], node['k'])
                            self.parse_detail(url, data, company)
                            time.sleep(random.randint(2, 3))
                        else:
                            break
                except Exception as E:
                    continue
                if len(data_dict['data']['dataList']) == 30 and Data['start'] < 134:
                    Data['start'] += 1
                    time.sleep(10)
                else:
                    break
            else:
                break

    def parse_detail(self, url, data, company):
        """
        提取数据
        :param data:
        :return:
        """
        while True:
            try:
                r = requests.get(url, headers=self.headers, proxies=self.get_proxy(), timeout=5)
                break
            except:
                pass
        try:
            data_dict = json.loads(r.content.decode())
            data['data'] = data_dict['data']
            data['detail'] = json.loads(data_dict['data']['detialJSonStr'])
        except Exception as E:
            return
        if '异常' in data_dict.get('message', ''):
            # print(data_dict)
            raise ValueError
        if '重新登录' in data_dict.get('message', ''):
            # print(data_dict)
            raise ValueError
        if data_dict['code'] != 1:
            # print(data_dict)
            raise ValueError
        item = {}
        item["输入公司名"] = company
        item['姓名'] = data['data']['userDetials']['userName']
        item['人才类型'] = data['detail'].get('tags')
        item['年龄'] = data['data']['userDetials']['birthYear']
        gender = data['data']['userDetials']['gender']
        if gender == '1':
            item['性别'] = '男'
        elif gender == '2':
            item['性别'] = '女'
        province = AREA.get(data['data']['userDetials']['provinceStateId']) if AREA.get(
            data['data']['userDetials']['provinceStateId']) else ''
        city = AREA.get(data['data']['userDetials']['cityId']) if AREA.get(
            data['data']['userDetials']['cityId']) else '-'
        item['现居住地'] = province + '-' + city
        item['简历id'] = data['data']['resumeNo']
        try:
            item['工作状态'] = WORKSTATUS.get(data['detail']['DesiredPosition'][0]['CurrentCareerStatus'])
        except:
            item['工作状态'] = '无'
        start_time = data['detail']['WorkExperience'][0]['DateStart'].split(' ')[0] + '-'
        end_time = data['detail']['WorkExperience'][0]['DateEnd'] if data['detail']['WorkExperience'][0][
                                                                         'DateEnd'] != '' else '至今'
        item['工作时间'] = start_time + end_time
        Salary = data['detail']['WorkExperience'][0].get('Salary')
        if Salary:
            item['工作薪资'] = str(int(Salary[:len(Salary) // 2].replace(Salary[:len(Salary) // 2][-1], '0'))) + '-' + str(
                int(Salary[len(Salary) // 2:]))
        else:
            item['工作薪资'] = '-'
        item['公司名称'] = data['detail']['WorkExperience'][0].get('CompanyName')
        item['公司行业'] = INDUSTRY.get(data['detail']['WorkExperience'][0]['CompanyIndustry']) if \
            data['detail']['WorkExperience'][0].get('CompanyIndustry') else '-'
        item['企业性质'] = NATURE.get(data['detail']['WorkExperience'][0]['CompanyProperty']) if \
            data['detail']['WorkExperience'][0].get('CompanyProperty') else '-'
        item['公司规模'] = SIZE.get(data['detail']['WorkExperience'][0]['CompanySize']) if data['detail']['WorkExperience'][
            0].get('CompanySize') else '-'
        item['工作职位'] = data['detail']['WorkExperience'][0].get('JobTitle')
        item['工作描述'] = data['detail']['WorkExperience'][0].get('WorkDescription').replace('\r\n', '') if \
            data['detail']['WorkExperience'][0].get('WorkDescription') else '-'
        item['更新时间'] = data['modifyDate']
        item['date'] = int(time.time())
        # print(item)
        self.col.insert(item)

    def run(self):
        try:
            for data, data1 in self.generator_data():
                company = data1['data']
                if self.sign == 0:
                    self.parse_list(data, company)
                    self.finish_list.append(data1['id'])
                    time.sleep(random.randint(2, 3))
                else:
                    break
            if self.sign == 0:
                SpiderTask.objects.finish_task2(self.task_id)
                print('{}爬取完成'.format(self.table_name))
            else:
                print('{}已中断'.format(self.table_name))
        except Exception as E:
            print(E)
            SpiderTask.objects.change_task2_status(task_id=self.task_id)
            print('{}已中断'.format(self.table_name))
