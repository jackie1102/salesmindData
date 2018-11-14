import copy
import random
import urllib.parse
import requests
from spider.runspider.liepin.liepin_basepider import LiePinBaseSpider
from spider.models import *
from lxml import etree


class LiePinCondition(LiePinBaseSpider):
    def __init__(self, param):
        super(LiePinCondition, self).__init__(param=param)
        self.param = param.get('param')
        self.start_page = param.get('start_page')
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

    def parse_list2(self):
        data = self.change_data()
        data['curPage'] = int(self.start_page)
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
                time.sleep(random.randint(5, 8))
            else:
                break

    def parse_list(self):
        data = self.change_data()
        data['curPage'] = int(self.start_page)
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
                data_list = []
                for node in nodes:
                    if 'http' not in node['resumeUrl']:
                        url = 'https://lpt.liepin.com' + node['resumeUrl']
                    else:
                        url = node['resumeUrl']
                    data_list.append(url)
                SpiderData.objects.add_data_list(data_list=data_list, task_id=self.task_id)
            if data['curPage'] < int(data_dict['data']['pageBarForm']['pageCount']) and self.sign == 0:
                data['curPage'] += 1
                time.sleep(random.randint(5, 8))
            else:
                break

    def run(self):
        if not self.type:
            try:
                self.parse_list()
                if self.sign == 0:
                    SpiderTask.objects.finish_task1(task_id=self.task_id)
                    print('{}完成'.format(self.table_name))
                else:
                    print('{}已中断'.format(self.table_name))
            except Exception as E:
                print(E)
                SpiderTask.objects.change_task1_status(task_id=self.task_id)
                print('{}已中断'.format(self.table_name))
            self.update_data_count()
        else:
            try:
                self.parse_list2()
                if self.sign == 0:
                    SpiderTask.objects.finish_task1(task_id=self.task_id)
                    task = SpiderTask.objects.get_one_task(id=self.task_id)
                    task.data_totle = 1
                    task.save()
                    SpiderTask.objects.finish_task2(task_id=self.task_id)
                    print('{}完成'.format(self.table_name))
                else:
                    print('{}已中断'.format(self.table_name))
            except Exception as E:
                print(E)
                SpiderTask.objects.change_task1_status(task_id=self.task_id)
                print('{}已中断'.format(self.table_name))


class LiePinConditionParse(LiePinBaseSpider):
    def __init__(self, param):
        super(LiePinConditionParse, self).__init__(param=param)
        self.all_work = param.get("all_work")

    def parse_detail(self, url, Data=None):
        while True:
            try:
                r = requests.get(url, headers=self.headers, timeout=10)
                con = r.content.decode()
                if '出错了' in con and '对企业不开放' not in con:
                    self.login()
                    continue
                html = etree.HTML(con)
                break
            except Exception as E:
                print(E)
                print(url)
                continue
        item = {}
        if Data:
            item['输入公司或ID'] = Data
        try:
            node = html.xpath('//div[@class="work-cont"]')[0]
        except:
            return None
        company = node.xpath('.//div[@class="work-cont-company-name"]/p[1]/span/text()')
        item['公司名'] = company[0] if len(company) > 0 else '-'
        status = html.xpath('//label[@class="labels labels-small labels-blunt labels-gray"]/span/text()')
        item['工作状态'] = status[0] if len(status) > 0 else ' '
        gender = html.xpath('//span[@class="individual-info-cont float-right"]/text()')
        try:
            item['性别'] = gender[0].split('·')[1] if len(gender) > 0 else ' '
        except:
            item['性别'] = ' '
        try:
            item['年龄'] = gender[0].split('·')[2] if len(gender) > 0 else ' '
        except:
            item['年龄'] = ' '
        try:
            item['目前年薪'] = \
                html.xpath('//section[@class="occupation-survey content-wrap"]/div[2]//tr[2]//p[1]/span[2]/text()')[0]
        except:
            item['目前年薪'] = ' '
        try:
            item['公司行业'] = \
                html.xpath('//section[@class="occupation-survey content-wrap"]/div[2]//tr[3]//p[1]/span[2]/text()')[0]
        except:
            item['公司行业'] = ' '
        try:
            item['所在地区'] = \
                html.xpath('//section[@class="occupation-survey content-wrap"]/div[2]//tr[4]//p[1]/span[2]/text()')[0]
        except:
            item['所在地区'] = ' '
        try:
            item['所在职位'] = \
                html.xpath('//section[@class="occupation-survey content-wrap"]/div[2]//tr[5]//p[1]/span[2]/text()')[0]
        except:
            item['所在职位'] = ' '
        info_cont = html.xpath('//span[@class="individual-info-cont current-status"]/text()')
        try:
            item['工作年限'] = info_cont[0].split('·')[2] if len(info_cont) > 0 else '-'
        except:
            item['工作年限'] = ' '
        id = html.xpath('//small[text()="简历编号："]/following-sibling::small/text()')
        item['简历ID'] = id[0] if len(id) > 0 else '-'
        update = html.xpath('//h6[@class="float-right"]/small/text()')
        item['更新时间'] = update[0].replace('更新', '') if len(update) > 0 else ' '
        worktime = node.xpath('.//div[@class="work-cont-company-name"]/p[2]/text()')
        item['工作时间'] = worktime[0].split('(')[0] if len(worktime) > 0 else '-'
        try:
            item['工作时长'] = worktime[0].split('(')[1].replace(')', '') if len(worktime) > 0 else '-'
        except:
            item['工作时长'] = ' '
        num = node.xpath('.//span[@class="num float-right filter-zone"]/text()')
        item['下属人数'] = num[0] if len(num) > 0 else ' '
        nod = node.xpath('.//div[@class="work-cont-list"]//span')
        achievement = nod[0].xpath('./text()') if nod else '-'
        item['职责业绩'] = ''.join(achievement).replace(' ', '').replace('\n', '').replace('\t', '')
        try:
            item['公司规模'] = node.xpath(
                './/div[@class="company-nature"]/label/span[contains(text(),"人") or contains(text(),"0") or contains(text(),"9")]/text()')[
                0]
        except:
            item['公司规模'] = ' '
        try:
            natures = node.xpath(
                './/div[@class="company-nature"]//text()')
            for nature in natures:
                if nature in [
                    '外商独资·外企办事处', '私营·民营企业', '国有企业', '中外合营(合资·合作)', '国内上市公司', '事业单位', 'Joint Venture·Cooperation',
                    'Private Enterprises', 'Domestic Listed Companies', 'State-owned Enterprise',
                    'Government Non-profit Organization', 'Foreign-funded·Foreign Office', 'Others'
                ]:
                    item['企业性质'] = nature
                    break
            else:
                item['企业性质'] = ' '
        except:
            item['企业性质'] = ' '
        try:
            item['所在部门'] = node.xpath('.//div[@class="work-cont-other"]/ul/li[2]/span[2]/text()')[0]
        except:
            item['所在部门'] = ' '
        try:
            item['汇报对象'] = node.xpath('.//div[@class="work-cont-other"]/ul/li[3]/span[2]/text()')[0]
        except:
            item['汇报对象'] = ' '
        try:
            item['tips'] = ''.join(html.xpath('//span[@class="text-warning"]/text()')).strip()
        except:
            item['tips'] = ' '
        item['date'] = int(time.time())
        return item

    def parse_detail_all(self, url, Data=None):
        while True:
            try:
                r = requests.get(url, headers=self.headers, timeout=10)
                con = r.content.decode()
                html = etree.HTML(con)
                if '出错了' in con:
                    self.login()
                    continue
                break
            except requests.RequestException:
                continue
        item = {}
        if Data:
            item['输入公司/ID'] = Data
        status = html.xpath('//label[text()="职业状态："]/../div/text()')
        item['工作状态'] = status[0] if len(status) > 0 else ' '
        gender = html.xpath('//label[text()="性别："]/../div/text()')
        item['性别'] = gender[0] if len(gender) > 0 else ' '
        age = html.xpath('//label[text()="年龄："]/../div/text()')
        item['年龄'] = age[0] if len(age) > 0 else ' '
        salary = html.xpath('//label[text()="目前年薪："]/../div/text()')
        item['目前年薪'] = salary[0] if len(salary) > 0 else ' '
        workyears = html.xpath('//label[text()="工作年限："]/../div/text()')
        item['工作年限'] = workyears[0] if len(workyears) > 0 else ' '
        id = html.xpath('//div[@class="more"]/span[1]/text()')
        item['简历ID'] = id[0].split('|')[0].replace('简历编号：', '').strip() if len(id) > 0 else ' '
        item['更新时间'] = id[0].split('|')[1].replace('更新日期：', '') if len(id) > 0 else ' '
        tip = html.xpath('//div[@class="alert alert-error"]/p/text()')
        tip2 = html.xpath('//div[@class="alert alert-error alert-inline"]/text()')
        if len(tip) > 0:
            item['标注'] = tip[0]
        elif len(tip2) > 0:
            item['标注'] = tip2[0]
        else:
            item['标注'] = ' '
        if '当前登录信息异常' in item['标注']:
            raise Exception
        while True:
            try:
                data2 = {'res_id_encode': item['简历ID']}
                r = requests.post('https://lpt.liepin.com/resume/getworkexps', data=data2, headers=self.headers)
                html1 = etree.HTML(r.text)
                break
            except requests.RequestException:
                continue
        if html1 is not None:
            nodes = html1.xpath('//div[@class="exp"]/table[@class="table table-noborder table-form"]')
            for node in nodes:
                item1 = copy.copy(item)
                worktime = node.xpath('.//th[@class="times"]/text()')
                item1['工作时间'] = worktime[0] if len(worktime) > 0 else ' '
                company_and_time = node.xpath('.//th[@class="section-content filter-zone"]/text()')[0]
                item1['公司名称'] = company_and_time.split(' ')[0]
                item1['工作时长'] = company_and_time.split(' ')[1]
                info = node.xpath('.//span[@class="comp-info"]/label[text()="公司描述："]/../text()')
                item1['公司描述'] = info[0] if len(info) > 0 else ' '
                nature = node.xpath('.//span[@class="comp-info"]/label[text()="公司性质："]/../text()')
                item1['公司性质'] = nature[0] if len(nature) > 0 else ' '
                scale = node.xpath('.//span[@class="comp-info"]/label[text()="公司规模："]/../text()')
                item1['公司规模'] = scale[0] if len(scale) > 0 else ' '
                industry = node.xpath('.//span[@class="comp-info"]/label[text()="公司行业："]/../text()')
                item1['公司行业'] = industry[0] if len(industry) > 0 else ' '
                position = node.xpath('.//h5/text()')
                item1['所在职位'] = position[0] if len(position) > 0 else ' '
                address = node.xpath('.//th[text()="所在地区："]/following-sibling::td[1]/text()')
                item1['所在地区'] = address[0] if len(address) > 0 else ' '
                branch = node.xpath('.//th[text()="所在部门："]/following-sibling::td/text()')
                item1['所在部门'] = branch[0] if len(branch) > 0 else ' '
                element = node.xpath('.//th[text()="汇报对象："]/following-sibling::td/text()')
                item1['汇报对象'] = element[0] if len(element) > 0 else ' '
                num = node.xpath('.//th[text()="下属人数："]/following-sibling::td[1]/text()')
                item1['下属人数'] = num[0] if len(num) > 0 else ' '
                achievement = node.xpath('.//th[text()="职责业绩："]/following-sibling::td[1]/text()')
                item1['职责业绩'] = ''.join(achievement).replace(' ', '').replace('\n', '').replace('\t', '')
                item1['date'] = int(time.time())
                self.col.insert(item1)

    def run(self):
        try:
            for data in self.get_data():
                url = data['data']
                if self.sign == 0:
                    if not self.all_work:
                        item = self.parse_detail(url)
                        if item:
                            self.col.insert(item)
                        self.finish_list.append(data['id'])
                        time.sleep(random.randint(3, 5))
                    else:
                        self.parse_detail_all(url)
                        self.finish_list.append(data['id'])
                        time.sleep(random.randint(3, 5))
                else:
                    break
            if self.sign == 0:
                SpiderTask.objects.finish_task2(task_id=self.task_id)
                print('{}完成'.format(self.table_name))
            else:
                print('{}中断'.format(self.table_name))
        except Exception as E:
            print(E)
            SpiderTask.objects.change_task2_status(task_id=self.task_id)
            print('{}中断'.format(self.table_name))
