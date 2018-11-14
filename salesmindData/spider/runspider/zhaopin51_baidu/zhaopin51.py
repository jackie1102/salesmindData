from threading import Thread
from lxml import etree
import requests
from db.base_spider import BaseSpider
from spider.models import *


class Spider(BaseSpider):
    def __init__(self, param):
        super(Spider, self).__init__(param=param)
        self.type = param.get('type')
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36'
        }

    def parse(self, data_list):
        for data in data_list:
            if self.type == '0':
                url = 'https://www.baidu.com/s?ie=utf-8&wd={}'.format(data['data'] + ' 智联招聘')
            else:
                url = 'https://www.baidu.com/s?ie=utf-8&wd={}'.format(data['data'] + ' 前程无忧')
            if self.sign == 0:
                url_list = self.parse_list(url)
                for detail_url in url_list:
                    if self.sign == 0:
                        if self.type == '0':
                            item = self.parse_detail_zhaopin(detail_url)
                        elif self.type == '1':
                            item = self.parse_detail_51(detail_url)
                        else:
                            item = None
                        if item:
                            item['输入公司名'] = data['data']
                            item['date'] = int(time.time())
                        self.col.insert_one(item)
                    else:
                        break
                if self.sign == 0:
                    self.finish_list.append(data['id'])
            else:
                break

    def parse_list(self, url):
        while True:
            try:
                res = requests.get(url, headers=self.headers, proxies=self.get_proxy(), timeout=3)
                break
            except:
                continue
        content = res.content.decode()
        html = etree.HTML(content)
        try:
            if self.type == '0':
                nodes = html.xpath('//a[contains(text(),"company.zhaopin.com")]/@href')
                url_list = nodes[:5] if len(nodes) > 4 else nodes
            elif self.type == '1':
                nodes = html.xpath('//a[contains(text(),"jobs.51job.com/all")]/@href')
                url_list = nodes[:5] if len(nodes) > 4 else nodes
            else:
                url_list = []
        except Exception as E:
            # print(E)
            url_list = []
        return url_list

    def parse_detail_zhaopin(self, url):
        res = requests.get(url, headers=self.headers)
        content = res.content.decode()
        html = etree.HTML(content)
        item = {}
        title = html.xpath('//h1[@class="detail-info__title__txt"]/text()')
        item['title'] = title[0].strip() if len(title) > 0 else ' '
        nature = html.xpath('//div[@class="detail-info__main__number clearfix"]/span[1]/text()')
        item['nature'] = nature[0] if len(nature) > 0 else ' '
        scale = html.xpath('//div[@class="detail-info__main__number clearfix"]/span[2]/text()')
        item['scale'] = scale[0] if len(scale) > 0 else ' '
        website = html.xpath('//p[@class="company-info__detail-info__url"]/a/text()')
        item['website'] = website[0] if len(website) > 0 else ' '
        industry = html.xpath('//div[@class="detail-info__main__number clearfix"]/span[3]/text()')
        item['industry'] = industry[0] if len(industry) > 0 else ' '
        addr = html.xpath('//p[@class="map-box__adress"]/span/text()')
        item['addr'] = addr[0] if len(addr) > 0 else ' '
        try:
            selecter = html.xpath('//div[@class="company-show__content"]')[0]
            info = selecter.xpath('string(.)').strip().replace('\xa0', '')
            item['info'] = info
        except Exception as E:
            # print(E)
            item['info'] = '-'
        # print(item)
        return item

    def parse_detail_51(self, url):
        while True:
            try:
                res = requests.get(url, headers=self.headers, proxies=self.get_proxy(), timeout=3)
                break
            except:
                continue
        content = res.content.decode('gbk', 'ignore')
        html = etree.HTML(content)
        item = {}
        company = html.xpath('//h1/text()')
        item['company'] = company[0].replace('\r', '').replace('\t', '').replace('\n', '') if len(company) > 0 else ' '
        try:
            data = ''.join(html.xpath('//p[@class="ltype"]//text()')).replace('\r', '').replace('\t', '').replace('\n',
                                                                                                                  '') \
                .replace('\xa0', '').replace(' ', '').split('|')
        except:
            data = None
        try:
            item['nature'] = data[0]
        except:
            item['nature'] = ' '
        try:
            item['scale'] = data[1]
        except:
            item['scale'] = ' '
        try:
            item['industry'] = data[2]
        except:
            item['industry'] = ' '
        info = html.xpath('//div[@class="con_txt"]')
        item['info'] = info[0].xpath('string(.)').strip().replace(' ', '').replace('\xa0', '') if len(info) > 0 else ' '
        addr = ''.join(html.xpath('//span[text()="公司地址："]/../text()'))
        item['addr'] = addr.replace('\r\n', '').strip().replace(' ', '') if len(addr) > 0 else ' '
        website = html.xpath('//span[text()="公司官网："]/../a/text()')
        item['website'] = website[0] if len(website) > 0 else ' '
        # print(item)
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
