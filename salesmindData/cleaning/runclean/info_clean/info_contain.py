from threading import Thread

from db.base_spider import BaseSpider
from spider.models import *


class InfoContain(BaseSpider):
    def __init__(self, param):
        super(InfoContain, self).__init__(param=param)
        self.keywords = param.get('keywords', '').split(' ')
        self.field = param.get('field')

    def parse(self, data_list):
        for data in data_list:
            if self.sign == 0:
                item = json.loads(data['data'])
                info = item[self.field]
                value = ''
                for keyword in self.keywords:
                    if keyword.upper() in info.upper():
                        value += keyword + '；'
                item['result'] = value
                item['date'] = int(time.time())
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
                print('{}已中断'.format(self.table_name))
        except Exception as E:
            print(str(E))
            SpiderTask.objects.change_task2_status(task_id=self.task_id)
            print('{}已中断'.format(self.table_name))

