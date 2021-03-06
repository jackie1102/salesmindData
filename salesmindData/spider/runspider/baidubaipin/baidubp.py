from threading import Thread

import re
from lxml import etree
from db.base_spider import BaseSpider
import requests
from spider.models import *


class BaiduBaipin(BaseSpider):
    """
    初始化属性
    """
    def __init__(self, param):
        super(BaiduBaipin, self).__init__(param=param)
        self.base_url = param.get('base_url')
        pattern_query = re.compile(r'query=(.*?)&')
        pattern_city = re.compile(r'city=(.*?)&')
        self.query = pattern_query.findall(self.base_url)[0]
        self.city = pattern_city.findall(self.base_url)[0]
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"
        }

    def parse_list(self):
        """
        解析列表页，返回每页url列表
        :param url:
        :return:
        """
        detail_url_list = []
        pn = 0
        url = self.base_url.split('&pn=')[0] + '&pn={}'
        while True:
            if self.sign == 0:
                parse_url = url.format(pn)
                print("parsing url:", parse_url)
                while True:
                    try:
                        response = requests.get(parse_url, headers=self.headers, proxies=self.get_proxy(), timeout=5)  # 发送请求
                        break
                    except requests.RequestException:
                        continue
                content = response.content.decode()
                items = json.loads(content)
                item_list = items['data']['urls']
                if item_list and self.sign == 0:
                    for item in item_list:
                        detail_url = 'https://zhaopin.baidu.com/szzw?id={}&query={}&city={}'.format(item, self.query, self.city)
                        detail_url_list.append(detail_url)
                    pn += 20
                else:
                    break
            else:
                break
        SpiderData.objects.add_data_list(data_list=detail_url_list, task_id=self.task_id)

    def run(self):
        """
        执行过程
        :return:
        """
        try:
            self.parse_list()
            if self.sign == 0:
                SpiderTask.objects.finish_task1(task_id=self.task_id)
                print('{}完成'.format(self.table_name))
            else:
                print('{}中断'.format(self.table_name))
        except Exception as E:
            print(E)
            SpiderTask.objects.change_task1_status(task_id=self.task_id)
            print('{}中断'.format(self.table_name))
        self.update_data_count()


class BaiDuBaiPinParse(BaseSpider):
    def __init__(self, param):
        super(BaiDuBaiPinParse, self).__init__(param=param)
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"
        }

    def parse_detail(self, url):
        """
        解析详情页
        :param url:
        :return:
        """
        while True:
            try:
                response = requests.get(url, headers=self.headers, proxies=self.get_proxy(), timeout=10)  # 发送请求
                break
            except:
                continue
        content = response.content.decode()  # 获取html字符串
        html = etree.HTML(content)
        item = {}
        title = html.xpath('//h4[@class="job-name"]/text()')
        if not title:
            return None
        item['标题'] = title[0] if len(title) > 0 else None
        num = html.xpath('//div[@class="job-require"]/span/text()')
        item['招聘人数'] = num[0].replace('招聘人数：', '') if num else ' '
        p_type = html.xpath('//div[@class="job-classfiy"]/p[1]/text()')
        item['职位类型'] = p_type[0].replace('职位类型：', '') if p_type else ' '
        addr = html.xpath('//div[@class="job-classfiy"]/p[5]/text()')
        item['工作地点'] = addr[0].replace('工作地点：', '') if p_type else ' '
        info = html.xpath('//div[@class="job-detail"]/p/text()')
        item['职位描述'] = info[0] if info else ' '
        address = html.xpath('//div[@class="job-addr"]/p[2]/text()')
        item['工作地址'] = address[0] if address else ' '
        date = html.xpath('//div[@class="source"]/text()')
        item['更新日期'] = '-'.join(date[0].split('-')[:2])
        source = html.xpath('//div[@class="source"]/span/text()')
        item['来源'] = source[0].replace('于', '') if source else ' '
        item['date'] = int(time.time())
        return item

    def parse(self, data_list):
        for data in data_list:
            detail_url = data['data']
            if self.sign == 0:
                item = self.parse_detail(detail_url)
                if item:
                    self.col.insert(item)
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
                print('{}完成'.format(self.table_name))
            else:
                print('{}已中断'.format(self.table_name))
        except Exception as E:
            print(E)
            SpiderTask.objects.change_task2_status(task_id=self.task_id)
            print('{}已中断'.format(self.table_name))

