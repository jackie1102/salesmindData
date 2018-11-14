import re
from threading import Thread

import requests
from db.base_spider import BaseSpider
from lxml import html
from spider.models import *
BASE_URL = 'http://company.jctrans.com/Company/List/0-0--12-95-0/1.html'


class Jincheng(BaseSpider):

    def __init__(self, param):
        super(Jincheng, self).__init__(param=param)
        start_url = param.get('start_url')
        self.base_url = re.sub(r'(\d+?)\.html',"{}.html", start_url)

    def total_page(self):
        sel = html.fromstring(requests.get(self.base_url.format(1)).text)
        total_page_num = sel.xpath('//div[@id="page_abc"]/span[@class="page_sum" and position()=last()-2]/text()')[0]
        total_page_num = re.search(r'\d+', total_page_num).group()
        return total_page_num

    def generate_url(self):
        total_page_num = self.total_page()
        for i in range(1, int(total_page_num)+1):
            url = self.base_url.format(i)
            yield url

    def parse(self, url):
        items = []
        r = requests.get(url).text
        sel = html.fromstring(r)
        for i in sel.xpath('//div[@class="com_name"]'):
            item = {}
            item['company'] = i.xpath('a/@title')[0]
            item['href'] = i.xpath('a/@href')[0]
            contact = i.xpath('p[@class="link_person"]/descendant::text()')
            item['contact'] = ''.join(str(i).strip().replace('联系人：', '') for i in contact)
            items.append(json.dumps(item))
        return items

    def run(self):
        try:
            for url in self.generate_url():
                if self.sign == 0:
                    items = self.parse(url)
                    SpiderData.objects.add_data_list(data_list=items, task_id=self.task_id)
                    time.sleep(10)
                else:
                    break
            if self.sign == 0:
                SpiderTask.objects.finish_task1(task_id=self.task_id)
                print('{}爬取完成'.format(self.table_name))
            else:
                print('{}已中断'.format(self.table_name))
        except Exception as E:
            print(E)
            SpiderTask.objects.change_task1_status(task_id=self.task_id)
            print('{}已中断'.format(self.table_name))
        finally:
            self.update_data_count()


class JinChenParse(BaseSpider):
    def __init__(self, param):
        super(JinChenParse, self).__init__(param=param)

    def parse_page(self, item):
        url = item['href']
        try:
            r = requests.get(url).text
        except:
            return None
        selector = html.fromstring(r)
        for i in selector.xpath('//ul[@class="fei"]/li'):
            a = i.xpath('span[@class="name"]/text()')
            pattern = re.compile(r'[\u3000\r\n ]')
            a = pattern.sub('', ''.join(str(i).strip() for i in a))
            b = i.xpath('b/text()|span[2]/text()|text()')
            b = ''.join(str(i).strip() for i in b)
            item[a] = b
            brief_introduction = selector.xpath('//div[@class="contxt"]/text()')
            item['brief-introduction'] = pattern.sub('', ''.join(
                str(i).strip().replace(' ', '') for i in brief_introduction))
            item['date'] = int(time.time())
        return item

    def parse(self, data_list):
        for data in data_list:
            if self.sign == 0:
                item = json.loads(data['data'])
                item = self.parse_page(item)
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
                t = Thread(target=self.parse, args=(data_list,))
                t.start()
                thread_list.append(t)
            for t in thread_list:
                t.join()
            if self.sign == 0:
                SpiderTask.objects.finish_task2(task_id=self.task_id)
                print('{}已完成'.format(self.table_name))
            else:
                print("{}已中断".format(self.table_name))
        except Exception as E:
            print(E)
            SpiderTask.objects.change_task2_status(task_id=self.task_id)
            print('{}已中断'.format(self.table_name))