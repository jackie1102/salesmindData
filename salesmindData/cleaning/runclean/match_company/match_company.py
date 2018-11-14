from threading import Thread
from cleaning.runclean.match_company.utls import *
from db.base_spider import BaseSpider
from spider.models import *
from pymysql import connect


class MatchCompany(BaseSpider):
    def __init__(self, param):
        super(MatchCompany, self).__init__(param=param)
        self.com1 = param.get('com1')
        self.com2 = param.get('com2')
        self.oldcom = param.get('oldcom')
        self.conn = connect(host='139.196.29.181', port=3306, user='root', password='SuperJoy000',
                            database='pythonsalesmind',
                            charset='utf8')
        self.cur = self.conn.cursor()
        self.cur.execute('select name from python_areas;')
        self.result = self.cur.fetchall()

    def rm_sign(self, data):
        sign_list = ['(', ')', '（', '）', ',', '，', '。', '.', ' ', '-', '_']
        for sign in sign_list:
            data = data.replace(sign, '')
        return data

    def filter_abbreviation(self, data):
        for sel in data_list:
            data = data.split(sel)[0]
        for replace_item in replace_list:
            data = data.replace(replace_item, '')
        area_list = []
        for area in self.result:
            area_list.append(area[0])
        area_list.sort(key=lambda i: len(i), reverse=True)
        for area in area_list:
            data = data.replace(area, '')
        return data

    def parse(self, data_list):
        for data in data_list:
            item = json.loads(data['data'])
            com1 = item[self.com1]
            com2 = item[self.com2]
            oldcom = item.get(self.oldcom, '')
            a = self.rm_sign(com1)
            b = self.rm_sign(com2)
            c = self.rm_sign(oldcom)
            if a == b:
                item['result'] = 'True'
            elif b and c and b == c:
                item['result'] = 'True'
            else:
                a = self.filter_abbreviation(com1)
                b = self.filter_abbreviation(com2)
                c = self.filter_abbreviation(oldcom)
                if a == '' and b == '':
                    item['result'] = '手动'
                elif b == '' and c == '':
                    item['result'] = '手动'
                elif a == b:
                    item['result'] = '手动'
                elif b == c:
                    item['result'] = '手动'
                else:
                    item['result'] = 'False'
            item['date'] = int(time.time())
            self.col.insert_one(item)
            self.finish_list.append(data['id'])

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
        except Exception as E:
            print(E)
            SpiderTask.objects.change_task2_status(self.task_id)
            print('{}已中断'.format(self.table_name))
