from threading import Thread
import requests
from lxml import etree
from spider.models import *
from db.base_spider import BaseSpider


class ZhilianRecruit(BaseSpider):
    def __init__(self, param):
        super(ZhilianRecruit, self).__init__(param=param)
        self.keywords = param.get('keywords')
        self.city = param.get('city')
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36',
        }

    def parse(self, page_list):
        for page in page_list:
            if self.sign == 0:
                url = 'https://fe-api.zhaopin.com/c/i/sou?start={}&pageSize=60&cityId={}&workExperience=-1&education=-1&companyType=-1&employmentType=-1&jobWelfareTag=-1&kw={}&kt=3'.format(
                    page * 60, self.city, self.keywords)
                while True:
                    try:
                        r = requests.get(url, headers=self.headers, proxies=self.get_proxy(),timeout=3)
                        break
                    except:
                        pass
                data = json.loads(r.text)
                if data['data']:
                    nodes = data['data']['results']
                    url_list = []
                    for node in nodes:
                        url = node['positionURL']
                        url_list.append(url)
                    SpiderData.objects.add_data_list(data_list=url_list, task_id=self.task_id)
            else:
                break

    def run(self):
        try:
            l = list(range(0, 100))
            cut_list = self.cut_list(l, 15)
            thread_list = []
            for page_list in cut_list:
                t = Thread(target=self.parse, args=(page_list,))
                t.start()
                thread_list.append(t)
            for t in thread_list:
                t.join()
            if self.sign == 0:
                SpiderTask.objects.finish_task1(task_id=self.task_id)
                print('{}已完成'.format(self.table_name))
            else:
                print('{}已中断'.format(self.table_name))
        except Exception as E:
            print(E)
            SpiderTask.objects.change_task1_status(task_id=self.task_id)
            print('{}已中断'.format(self.table_name))
        finally:
            self.update_data_count()


class ZhilianRecruitParse(BaseSpider):
    def __init__(self, param):
        super(ZhilianRecruitParse, self).__init__(param=param)
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36',
        }

    def parse(self, data_list):
        for data in data_list:
            if self.sign == 0:
                url = data['data']
                item = self.parse_detail(url)
                self.col.insert_one(item)
                self.finish_list.append(data['id'])
            else:
                break

    def parse_detail(self, url):
        while True:
            try:
                r = requests.get(url, headers=self.headers, proxies=self.get_proxy(), timeout=3)
                break
            except:
                pass
        html = etree.HTML(r.text)
        item = {}
        company = html.xpath('//div[@class="company-box"]/p/a/text()')
        item['公司名'] = company[0] if company else '-'
        industry = html.xpath('//div[@class="company-box"]/ul/li[3]/strong/a/text()')
        item['行业'] = industry[0] if industry else '-'
        nature = html.xpath('//div[@class="company-box"]/ul/li[1]/strong/text()')
        item['企业性质'] = nature[0] if nature else '-'
        num = html.xpath('//div[@class="company-box"]/ul/li[2]/strong/text()')
        item['公司规模'] = num[0] if num else '-'
        addr = html.xpath('//div[@class="company-box"]/ul/li[4]/strong/text()')
        item['公司地址'] = addr[0].replace('\n', '') if addr else '-'
        item['date'] = int(time.time())
        return item

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
                print('{}已中断'.format(self.table_name))
        except Exception as E:
            print(E)
            SpiderTask.objects.change_task2_status(task_id=self.task_id)
            print('{}已中断'.format(self.table_name))



if __name__ == '__main__':
    data = {
        'keywords': ''
    }
    spider = ZhilianRecruit(data)