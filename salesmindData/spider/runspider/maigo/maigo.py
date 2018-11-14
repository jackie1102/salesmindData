from threading import Thread

from spider.models import *
from db.base_spider import BaseSpider
import re
import time
import requests
from scrapy.selector import Selector


class MaiGo(BaseSpider):
    def __init__(self, param):
        super(MaiGo, self).__init__(param=param)
        self.base_url = param.get('base_url')
        self.type = param.get('type')
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36',
            'Host': 'www.maigoo.com'
        }

    def make_url(self):
        pattern1 = re.compile(r'page%3A\d+')
        pattern2 = re.compile(r't=\d+')
        base_url = re.sub(pattern1, 'page%3A{}', self.base_url)
        base_url = re.sub(pattern2, 't={}', base_url)
        return base_url

    def parse_list(self):
        page = 1
        ur = self.make_url()
        while True:
            if self.sign == 0:
                url = ur.format(page, int(time.time() * 1000))
                while True:
                    try:
                        r = requests.get(url, headers=self.headers, proxies=self.get_proxy(), timeout=3)
                        html = Selector(r)
                        break
                    except Exception:
                        continue
                nodes = html.xpath('//dd')
                for node in nodes:
                    item = {}
                    item['产品名'] = node.xpath('.//span[@class="font18"]/a/text()').extract_first()
                    info = node.xpath('.//div[@class="desc dhidden"]/text()').extract_first().strip()
                    item['公司名'] = info.split('（')[0]
                    item['官网'] = node.xpath('.//a[text()="企业官方网站"]/@href').extract_first()
                    item['网店数量'] = node.xpath('.//a[contains(text(),"【网店")]/text()').extract_first(default='').replace('【网店', '').replace('】','')
                    item['简介'] = info
                    item['标签'] = ';'.join(node.xpath('.//div[@class="result_foot font12 c666"]/a/text()').extract())
                    item['date'] = int(time.time())
                    self.col.insert(item)
                if len(nodes) != 0:
                    page += 1
                else:
                    break
            else:
                break

    def parse_(self):
        page = 1
        ur = self.make_url()
        while True:
            if self.sign == 0:
                url = ur.format(page, int(time.time()*1000))
                while True:
                    try:
                        r = requests.get(url, headers=self.headers, proxies=self.get_proxy(), timeout=3)
                        html = Selector(r)
                        break
                    except Exception:
                        continue
                nodes = html.xpath('//a[@class="c3f6799 b"]/@href').extract()
                SpiderData.objects.add_data_list(data_list=nodes, task_id=self.task_id)
                if len(nodes) != 0:
                    page += 1
                else:
                    break
            else:
                break

    def run(self):
        try:
            if self.type == '0':
                self.parse_list()
            elif self.type == '1':
                self.parse_()
            if self.sign == 0:
                SpiderTask.objects.finish_task1(task_id=self.task_id)
                task = SpiderTask.objects.get_one_task(id=self.task_id)
                task.data_totle = 1
                task.save()
                print('{}已完成'.format(self.table_name))
            else:
                print('{}已中断'.format(self.table_name))
        except Exception as E:
            print(E)
            SpiderTask.objects.change_task1_status(task_id=self.task_id)
            print('{}已中断'.format(self.table_name))
        if self.type == '1':
            self.update_data_count()


class MaiGoParse(BaseSpider):
    def __init__(self, param):
        super(MaiGoParse, self).__init__(param=param)
        self.type = param.get('type')
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36',
            'Host': 'www.maigoo.com'
        }

    def parse_detail(self, url, data=None):
        item = {}
        while True:
            try:
                r = requests.get(url, headers=self.headers, proxies=self.get_proxy(), timeout=3)
                html = Selector(r)
                break
            except Exception:
                continue
        if data:
            item['搜索公司'] = data
        item['公司名'] = html.xpath('//*[@id="brandinfo"]//*[contains(@class,"font16")]/text()').extract_first(default='').replace('（', '').replace('）', '')
        item['产品名'] = html.xpath('//*[@id="brandinfo"]//span[@class="font22 line18em b"]/text()').extract_first()
        item['公司简介'] = ''.join(html.xpath('//*[@id="container"]//div[@class="branddesc"]/div[2]//text()').extract()).replace('\n', '')
        try:
            item['联系方式'] = html.xpath('//span[contains(text(),"联系方式：")]/text()').extract()[1]
        except:
            item['联系方式'] = ' '
        item['品牌发源地'] = html.xpath('//span[contains(text(),"品牌发源地：")]/text()').extract_first(default='').replace('品牌发源地：', '')
        item['品牌创立时间'] = html.xpath('//span[contains(text(),"品牌创立时间：")]/text()').extract_first(default='').replace('品牌创立时间：', '')
        item['行业分类'] = html.xpath('//span[text()="十大品牌"]/following-sibling::a/text()').extract_first()
        item['相关品牌'] = ';'.join(html.xpath('//em[@class="font14 dhidden"]/text()').extract())
        shop_more = html.xpath('//dt[@title="品牌网店"]/following-sibling::dd/a/@href').extract_first()
        if shop_more and shop_more != '':
            shop_id = shop_more.split('shop_')[1].replace('.html', '')
            data, data_num = self.get_shop(shop_id)
            item['品牌网店'] = data
            item['网点数量'] = data_num
        else:
            item['品牌网店'] = '-'
            item['网点数量'] = '-'
        item['date'] = int(time.time())
        return item

    def get_shop(self, shop_id):
        shop_base_url = 'http://www.maigoo.com/ajaxstream/loadblock/?str=webshop%3Acol1_brandid%3A{}%2Ccatid%3A-%2Cnum%3A10%2Cpage%3A{}&append=1&t={}'
        page = 1
        data = ''
        data_num = 0
        while True:
            url = shop_base_url.format(shop_id, page, int(time.time() * 1000))
            while True:
                try:
                    r = requests.get(url, headers=self.headers, proxies=self.get_proxy(), timeout=3)
                    html = Selector(r)
                    break
                except Exception:
                    continue
            nodes = html.xpath('//a[@class="font16"]')
            for node in nodes:
                shop_name = node.xpath('./text()').extract_first()
                shop_url = node.xpath('./@href').extract_first()
                shop = '{}:{};'.format(shop_name, shop_url)
                data += shop
                data_num += 1
            if len(nodes) == 10:
                page += 1
            else:
                break
        return data, data_num

    def parse(self, data_list):
        for data in data_list:
            url = data['data']
            if self.sign == 0:
                item = self.parse_detail(url=url)
                self.col.insert_one(item)
                self.finish_list.append(data['id'])
            else:
                break

    def run(self):
        try:
            if self.type == '0':
                SpiderTask.objects.finish_task2(task_id=self.task_id)
            else:
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
