import random
import requests
from lxml import etree
from spider.models import *
from spider.runspider.job51_.base_job import BaseJob


class JobCK(BaseJob):
    def __init__(self, param):
        super(JobCK, self).__init__(param=param)
        self.data = param.get('param')

    def get_cookie(self):
        if self.param.get('login_cookie'):
            self.username_id = self.param.get('username_id')
            self.user = JobId.objects.get_one_ID_by_id(self.username_id)
            self.vipname = self.user.vipname
            self.username = self.user.username
            self.password = self.user.password
            self.headers = {
                'Cookie': self.param.get('login_cookie'),
                'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'
            }
        else:
            while True:
                users = JobId.objects.get_data_list_by_status(0)
                if users:
                    self.user = random.choice(users)
                    self.vipname = self.user.vipname
                    self.username = self.user.username
                    self.password = self.user.password
                    self.username_id = self.user.id
                    cookie = self.login()
                    task = SpiderTask.objects.get_one_task(id=self.task_id)
                    data = json.loads(task.param)
                    data["login_cookie"] = cookie
                    data['username_id'] = self.username_id
                    task.param = json.dumps(data)
                    task.save()
                    self.headers = {
                        'Cookie': cookie,
                        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'
                    }
                    break
                else:
                    time.sleep(300)
            self.user.status = 1
            self.user.task_id = self.task_id
            self.user.save()

    def parse_(self, company):
        r = requests.get('https://ehire.51job.com/Candidate/SearchResumeNew.aspx', headers=self.headers, verify=False)
        html = etree.HTML(r.text)
        viewstate = html.xpath('//*[@id="__VIEWSTATE"]/@value')[0]
        data = {
            '__EVENTTARGET': 'ctrlSerach$search_submit',
            'ctrlSerach$hidSearchValue': self.data.format(company),
            '__VIEWSTATE': viewstate
        }
        page = 1
        item_list = []
        while True:
            if self.sign == 0:
                r = requests.post('https://ehire.51job.com/Candidate/SearchResumeNew.aspx', headers=self.headers,
                                  data=data,
                                  verify=False)
                html = etree.HTML(r.text)
                nodes = html.xpath('//tr[contains(@id, "trBaseInfo")]')
                if len(nodes) == 0:
                    break
                print(page)
                for node in nodes:
                    if self.sign == 0:
                        try:
                            url = node.xpath('.//td[2]/span/a/@href')[0]
                        except Exception as e:
                            print(e)
                            continue
                        if 'https:' not in url:
                            url = 'https://ehire.51job.com' + url
                        item = self.parse_detail(url)
                        item_list.append(item)
                        time.sleep(random.randint(3,5))
                    else:
                        break
                viewstate = html.xpath('//*[@id="__VIEWSTATE"]/@value')[0]
                data['__VIEWSTATE'] = viewstate
                data['__EVENTTARGET'] = 'pagerBottomNew$nextButton'
                time.sleep(3)
                page += 1
            else:
                break
        return item_list

    def parse_detail(self, url):
        while True:
            r = requests.get(url, headers=self.headers)
            if 'Login' in r.url:
                print('Cookie已过期, 重新获取cookie')
                self.release()
                cookie = self.login()
                self.headers['Cookie'] = cookie
                continue
            html = etree.HTML(r.text)
            try:
                cookie = self.check_YZM(html, url)
                if cookie:
                    self.headers['Cookie'] = cookie
                else:
                    break
            except Exception as E:
                print(E)
        html = etree.HTML(r.text)
        item = {}
        try:
            item['ID'] = html.xpath('//span[contains(text(), "ID:")]/text()')[0].strip().replace('ID:', '')
        except:
            item['ID'] = ' '
        try:
            item['更新时间'] = html.xpath('//*[@id="lblResumeUpdateTime"]/b/text()')[0]
        except:
            item['更新时间'] = ' '
        try:
            item['目前状况'] = ''.join(html.xpath('//table[@class="infr"]//tr[2]/td[1]/text()')).strip()
        except:
            item['目前状况'] = ' '
        try:
            item['到岗时间'] = html.xpath('//td[text()="到岗时间："]/following-sibling::td[1]/text()')[0]
        except:
            item['到岗时间'] = ' '
        try:
            item['目前薪水'] = html.xpath('//td[contains(text(),"目前年收入")]/span[1]/text()')[0].strip()
        except:
            item['目前薪水'] = ' '
        try:
            info = ''.join(html.xpath('//table[@class="infr"]//tr[3]/td//text()'))
        except:
            info = None
        if info:
            try:
                item['年龄'] = info.split('|')[1].split('（')[0]
            except:
                item['年龄'] = ' '
            try:
                item['现居住地'] = info.split('|')[2].replace('现居住', '').strip()
            except:
                item['现居住地'] = ' '
        else:
            item['年龄'] = ' '
            item['现居住地'] = ' '
        try:
            node = html.xpath('//td[text()="工作经验"]/../../tr[2]/td/table//tr')[0]
        except:
            node = html.xpath('//*[@id="lblResumeUpdateTime"]/b')[0]
        try:
            item['公司名'] = node.xpath('.//span[@class="bold"]/text()')[0]
        except:
            item['公司名'] = ' '
        try:
            item['工作时间'] = node.xpath('.//tr[1]/td[@class="time"]/text()')[0]
        except:
            item['工作时间'] = ' '
        try:
            item['工作年限'] = node.xpath('.//span[@class="gray"]/text()')[0].replace(' ', '').replace('\r\n', '')
        except:
            item['工作年限'] = ' '
        try:
            item['职位'] = node.xpath('.//td[@class="rtbox"]/strong/text()')[0]
        except:
            item['职位'] = ' '
        try:
            item['行业'] = node.xpath('//td[text()="行　业："]/following-sibling::td/text()')[0]
        except:
            item['行业'] = ' '
        try:
            item['工作描述'] = node.xpath('.//td[text()="工作描述："]/following-sibling::td/text()')[0]
        except:
            item['工作描述'] = ' '
        try:
            item['公司规模'] = ''.join(node.xpath('.//tr[2]/td[@class="rtbox"]//text()')).split('|')[1]
        except:
            item['公司规模'] = ' '
        try:
            item['公司性质'] = ''.join(node.xpath('.//tr[2]/td[@class="rtbox"]//text()')).split('|')[2]
        except:
            item['公司性质'] = ' '
        item['date'] = int(time.time())
        return item

    def run(self):
        try:
            for data in self.get_data():
                if self.sign == 0:
                    item_list = self.parse_(data['data'])
                    self.col.insert(item_list)
                    self.finish_list.append(data['id'])
                else:
                    break
            if self.sign == 0:
                SpiderTask.objects.finish_task2(task_id=self.task_id)
                print('{}-详情采集完成'.format(self.table_name))
            else:
                print('{}-详情采集中断'.format(self.table_name))
        except Exception as E:
            print(str(E))
            SpiderTask.objects.change_task2_status(self.task_id)
            print('{}-详情采集中断')
        self.release()