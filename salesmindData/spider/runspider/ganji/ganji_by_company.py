from threading import Thread

import requests
from lxml import etree
from db.base_spider import BaseSpider
from spider.models import *


class Spider(BaseSpider):

    def __init__(self, param):
        super(Spider, self).__init__(param=param)
        self.base_url = param.get('base_url')
        self.headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36',
        }

    def parse_list(self, url):
        url_list = []
        url_ = url
        while True:
            if self.sign == 0:
                while True:
                    try:
                        r = requests.get(url, headers=self.headers, proxies=self.get_proxy(), timeout=10)
                        html = etree.HTML(r.content.decode())
                        break
                    except:
                        continue
                text = html.xpath('//p[contains(text(),"抱歉")]')
                if len(text) > 0:
                    break
                nodes = html.xpath('//dl[contains(@class,"con-list-zcon")]')
                for node in nodes:
                    detail_url = node.xpath('./dt/a/@href')[0]
                    url_list.append(detail_url)
                try:
                    url_ = html.xpath('//span[text()="下一页"]/../@href')[0]
                    continue
                except Exception as E:
                    print(E)
                    break
            else:
                break
        return url_list

    def parse_detail(self, url):
        while True:
            try:
                r = requests.get(url, headers=self.headers, proxies=self.get_proxy(), timeout=10)
                html = etree.HTML(r.content.decode())
                break
            except requests.RequestException:
                continue
        item = {}
        title = html.xpath('//div[@class="title-line clearfix"]')
        item['title'] = title[0].xpath('string(.)').strip().replace('\n', '').replace(' ', '') if len(title) > 0 else ' '
        zhaopin_num = html.xpath('//div[@class="description-label"]/span[1]/text()')
        item['zhaopin_num'] = zhaopin_num[0] if len(zhaopin_num) > 0 else ' '
        addr = html.xpath('//div[@class="location-line clearfix"]/p/text()')
        item['addr'] = ''.join(a.replace(' ', '').replace('\n', '') for a in addr) if len(addr) > 0 else ' '
        company = html.xpath('//div[@class="company-info"]/h3/a/text()')
        item['company'] = company[0] if len(company) > 0 else ' '
        industry = html.xpath('//div[@class="introduce"]/span[3]/text()')
        item['industry'] = industry[0] if len(industry) > 0 else ' '
        nature = html.xpath('//div[@class="introduce"]/span[2]/text()')
        item['nature'] = nature[0] if len(nature) > 0 else ' '
        scale = html.xpath('//div[@class="introduce"]/span[1]/text()')
        item['scale'] = scale[0] if len(scale) > 0 else ' '
        company_id = html.xpath('//div[@class="company-info"]/h3/a/@href')[0].split('gongsi/')[1].replace('/', '')
        data = {
            'company_id': company_id,
            'user_id': '700888295',
        }
        res = requests.post('http://sh.ganji.com/ajax.php?_pdt=zhaopin&module=getHighQualityCompanyInfo', data=data)
        json_data = json.loads(res.content)
        zhaopin_pos_num = json_data['body']['postsCount']
        item['zhaopin_pos_num'] = zhaopin_pos_num
        zhaopin_info = html.xpath('//div[@class="description-content"]')
        item['zhaopin_info'] = zhaopin_info[0].xpath('string(.)').strip().replace(' ', '').replace('\r', '') if len(zhaopin_info) > 0 else ' '
        company_info = html.xpath('//div[@class="info-text"]/div/text()')
        item['company_info'] = ''.join(company_info).replace(' ', '').replace('\r', '').replace('\n', '') if len(company_info) > 0 else ' '
        item['date'] = int(time.time())
        return item

    def parse(self, data_list):
        for data in data_list:
            if self.sign == 0:
                url = self.base_url.format(data['data'])
                url_list = self.parse_list(url)
                if len(url_list) > 0:
                    for detail_url in url_list:
                        if self.sign == 0:
                            item = self.parse_detail(detail_url)
                            self.col.insert_one(item)
                            time.sleep(2)
                        else:
                            break
                    if self.sign == 0:
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



