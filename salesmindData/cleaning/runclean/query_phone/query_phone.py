import requests
from lxml import etree
from spider.models import *
from db.base_spider import BaseSpider


class Spider(BaseSpider):
    def __init__(self, param):
        super(Spider, self).__init__(param=param)
        self.field = param.get('field')
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36'
        }

    def parse_list(self, item):
        try:
            r = requests.get('https://www.baidu.com/s?wd={}'.format(int(item.get(self.field, ''))), headers=self.headers, verify=False)
        except:
            return None
        html = etree.HTML(r.text)
        addr = html.xpath('//div[@class="op_fraudphone_row"]/span[2]/text()|//div[@class="op_mobilephone_r c-gap-bottom-small"]/span[2]/text()')
        item['归属地'] = addr[0].split('\xa0\xa0')[0].replace('\xa0', ' ') if len(addr) > 0 else ' '
        tip = html.xpath('//div[@class="op_fraudphone_word"]//text()')
        item['标注'] = ''.join(tip).strip().replace('\xa0', '')
        item['date'] = int(time.time())
        return item

    def run(self):
        try:
            for data in self.get_data():
                if self.sign == 0:
                    item = self.parse_list(json.loads(data['data']))
                    if item:
                        item['date'] = int(time.time())
                        self.col.insert(item)
                    self.finish_list.append(data['id'])
                else:
                    break
            if self.sign == 0:
                SpiderTask.objects.finish_task2(task_id=self.task_id)
                print('{}已完成'.format(self.table_name))
            else:
                print('{}已中断'.format(self.table_name))
        except Exception as E:
            print(E)
            SpiderTask.objects.change_task2_status(task_id=self.task_id)
            print('{}已中断'.format(self.table_name))
