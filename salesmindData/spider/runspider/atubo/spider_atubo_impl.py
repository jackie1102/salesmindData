import random
from lxml import etree
import requests
from spider.models import *
from db.base_spider import BaseSpider
from threading import Thread


class ATUBO(BaseSpider):

    def __init__(self, param):
        super(ATUBO, self).__init__(param)
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36',
        }

    def parse_detail(self, detail_url, company=None, company_name=None):
        # print(detail_url)
        for i in range(5):
            try:
                r = requests.get(detail_url, headers=self.headers, proxies=self.get_proxy(), timeout=random.randint(3, 5), verify=False)
                text = r.content.decode('gbk', 'ignore')
                html = etree.HTML(text)
                try:
                    text = html.xpath('//*[@id="Context"]/div[2]/h1/text()')[0]
                    continue
                except:
                    break
            except Exception as E:
                continue
        else:
            return None
        item = {}
        item['搜索公司'] = company
        try:
            item['爬取公司'] = company_name
        except:
            item['爬取公司'] = ' '
        item['公司url'] = detail_url
        try:
            item['地址'] = html.xpath('//li[text()="地址："]/../li[2]/text()')[0]
        except:
            item['地址'] = ' '
        try:
            item['主营'] = html.xpath('//li[text()="主营："]/../li[2]/text()')[0]
        except:
            item['主营'] = ' '
        try:
            item['电话'] = html.xpath('//li[text()="电话："]/../li[2]/text()')[0]
        except:
            item['电话'] = ' '
        try:
            item['手机'] = html.xpath('//li[text()="手机："]/../li[2]/text()')[0]
        except:
            item['手机'] = ' '
        try:
            item['联系'] = html.xpath('//li[text()="联系："]/../li[2]/text()')[0]
        except:
            item['联系'] = ' '
        try:
            item['关于我们'] = html.xpath('//div[@class="aboutus"]/text()')[1]
        except:
            item['关于我们'] = ' '
        item['date'] = int(time.time())
        return item

    def parse_(self, company):
        try:
            data = {
                'Keyword': company.encode('gbk'),
                'Country': 0,
                'province': 0,
                'city': 0,
                'Lb': 0,
                'Buy_Type': 9,
            }
        except:
            print(company)
            return
        for i in range(5):
            try:
                r = requests.post('https://www.atobo.com.cn/Companys/Search_Redirect.aspx', data=data, headers=self.headers, proxies=self.get_proxy(), timeout=random.randint(3,5), verify=False)
                html = etree.HTML(r.text)
                break
            except requests.RequestException as E:
                # print(E)
                continue
        else:
            return
        try:
            detail_url = 'https://www.atobo.com.cn' + html.xpath('//ul/li[1]/a[@class="CompanyName"]/@href')[0]
            company_name = html.xpath('//ul/li[1]/a[@class="CompanyName"]/text()')[0]
        except:
            detail_url = None
            company_name = None
        if detail_url and company_name:
            item = self.parse_detail(detail_url, company, company_name)
            if item:
                self.col.insert_one(item)

    def parse(self, data_list):
        for data in data_list:
            if self.sign == 0:
                self.parse_(data['data'])
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
                SpiderTask.objects.finish_task2(self.task_id)
                print('{}爬取完成'.format(self.table_name))
            else:
                print('{}已中断'.format(self.table_name))
        except Exception as E:
            print(E)
            SpiderTask.objects.change_task2_status(self.task_id)
            print('{}已中断'.format(self.table_name))


class ConditionAtuBo(BaseSpider):

    def __init__(self, param):
        super(ConditionAtuBo, self).__init__(param)
        self.search_url = param.get('base_url')
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36',
        }

    def parse_list(self):
        while True:
            try:
                r = requests.get(self.search_url, headers=self.headers, proxies=self.get_proxy(),timeout=random.randint(3, 5), verify=False)
                html = etree.HTML(r.content.decode('gbk', 'ignore'))
                break
            except requests.RequestException:
                continue
        while True:
            if self.sign == 0:
                url_list = html.xpath('//a[@class="CompanyName"]/@href')
                try:
                    url = html.xpath('//a[@class="downpage"]/@href')[0]
                    if url != '#':
                        next_url = 'http://www.atobo.com.cn' + html.xpath('//a[@class="downpage"]/@href')[0]
                    else:
                        next_url = None
                except:
                    next_url = None
                SpiderData.objects.add_data_list(data_list=url_list, task_id=self.task_id)
                if next_url and self.sign == 0:
                    while True:
                        try:
                            r = requests.get(next_url, headers=self.headers, proxies=self.get_proxy(), timeout=random.randint(3, 5), verify=False)
                            html = etree.HTML(r.content.decode('gbk', 'ignore'))
                            break
                        except:
                            continue
                else:
                    break
            else:
                break

    def run(self):
        try:
            self.parse_list()
            if self.sign == 0:
                SpiderTask.objects.finish_task1(self.task_id)
                print('{}爬取完成'.format(self.table_name))
            else:
                print('{}已中断'.format(self.table_name))
        except Exception as E:
            print(E)
            SpiderTask.objects.change_task1_status(self.task_id)
            print('{}已中断'.format(self.table_name))
        self.update_data_count()


class ConditionAtuBoParse(BaseSpider):
    def __init__(self, param):
        super(ConditionAtuBoParse, self).__init__(param)
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36',
        }

    def parse_detail(self, detail_url):
        for i in range(5):
            try:
                res = requests.get(detail_url, headers=self.headers, proxies=self.get_proxy(), timeout=random.randint(3, 5), verify=False)
                text = res.content.decode('gbk', 'ignore')
                html = etree.HTML(text)
                break
            except requests.RequestException:
                continue
        else:
            return None
        item = {}
        try:
            item['爬取公司'] = html.xpath('//li[@class="logotext"]/p/em/text()')[0]
        except:
            item['爬取公司'] = ' '
        item['公司url'] = res.url
        try:
            item['地址'] = html.xpath('//li[text()="地址："]/../li[2]/text()')[0]
        except:
            item['地址'] = ' '
        try:
            item['主营'] = html.xpath('//li[text()="主营："]/../li[2]/text()')[0]
        except:
            item['主营'] = ' '
        try:
            item['电话'] = html.xpath('//li[text()="电话："]/../li[2]/text()')[0]
        except:
            item['电话'] = ' '
        try:
            item['手机'] = html.xpath('//li[text()="手机："]/../li[2]/text()')[0]
        except:
            item['手机'] = ' '
        try:
            item['联系'] = html.xpath('//li[text()="联系："]/../li[2]/text()')[0]
        except:
            item['联系'] = ' '
        try:
            item['关于我们'] = html.xpath('//div[@class="aboutus"]/text()')[1]
        except:
            item['关于我们'] = ' '
        item['date'] = int(time.time())
        return item

    def parse(self,data_list):
        for data in data_list:
            url = data['data']
            if self.sign == 0:
                if 'http' not in url:
                    url_ = 'https:' + url
                else:
                    url_ = url
                item = self.parse_detail(url_)
                if item:
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
                t = Thread(target=self.parse,args=(data_list,))
                t.start()
                thread_list.append(t)
            for t in thread_list:
                t.join()
            if self.sign == 0:
                SpiderTask.objects.finish_task2(self.task_id)
                print('{}爬取完成'.format(self.table_name))
        except Exception as E:
            print(E)
            SpiderTask.objects.change_task2_status(self.task_id)
            print('{}已中断'.format(self.table_name))
