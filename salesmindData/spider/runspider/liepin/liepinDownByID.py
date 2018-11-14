import requests
from scrapy.selector import Selector
from db.base_spider import BaseSpider
from spider.models import *
from spider.runspider.liepin.liepin_basepider import LiePinBaseSpider


class DownById(LiePinBaseSpider):
    def __init__(self, param):
        super(DownById, self).__init__(param=param)

    def parse_list(self, ID):
        while True:
            try:
                Data = {"pageSize": '20', "searchKey": "", "filterKey": "", "curPage": '0', "keys": ""}
                Data['keys'] = ID
                r = requests.post('https://lpt.liepin.com/resstore/so/', data=Data, headers=self.headers)
                if '异常' in r.text:
                    self.login()
                    continue
                html = Selector(r)
                break
            except:
                continue
        node = html.xpath('//div[@class="job-data1"]/a/@href').extract_first()
        if node:
            if 'http' not in node:
                detail_url = 'https://lpt.liepin.com' + node
            else:
                detail_url = node
            return detail_url
        else:
            return None

    def parse_detail(self, url):
        while True:
            try:
                r = requests.get(url, headers=self.headers)
                if '出错了' in r.text:
                    self.login()
                    continue
                html = Selector(r)
                break
            except:
                continue
        item = {}
        item['简历编号'] = html.xpath('//h6/small[2]/text()').extract_first(default=' ')
        item['更新日期'] = html.xpath('//h6/small/text()').extract()[2]
        item['姓名'] = html.xpath('//span[@class="individual-info-cont float-right"]/text()').extract_first(default=' ').split(' · ')[0]
        try:
            item['手机号码'] = html.xpath('//span[@class="individual-info-cont"]/em/text()').extract()[0]
        except:
            item['手机号码'] = ' '
        try:
            item['电子邮件'] = html.xpath('//span[@class="individual-info-cont"]/em/text()').extract()[1]
        except:
            item['电子邮件'] = ' '
        item['职业状态'] = html.xpath('//label[@class="labels labels-small labels-blunt labels-gray"]/span/text()').extract_first(default=' ')
        item['工作时间'] = html.xpath('//p[@class="time filter-zone"]/text()').extract_first(default=' ')
        item['公司名称'] = \
            html.xpath('//div[@class="work-cont-company-name"]/p/span/text()').extract_first(default=' ')
        item['职位'] = html.xpath('//div[@class="work-cont-company-certify clearfix"]/p/text()').extract_first(default=' ')
        nodes = html.xpath('//span[@class="filter-zone content"]')
        if nodes:
            node = nodes[0]
            item['职位描述'] = ''.join(node.xpath('./text()').extract())
        else:
            item['职位描述'] = ' '
        item['date'] = int(time.time())
        return item

    def run(self):
        try:
            for ID in self.get_data():
                if self.sign == 0:
                    detail_url = self.parse_list(ID['data'])
                    if detail_url:
                        item = self.parse_detail(detail_url)
                        if item:
                            self.col.insert_one(item)
                    self.finish_list.append(ID['id'])
                    time.sleep(5)
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

