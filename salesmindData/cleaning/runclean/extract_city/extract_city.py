from threading import Thread
from spider.models import *
from pymysql import connect
from db.base_spider import BaseSpider


class Clean(BaseSpider):
    def __init__(self, param):
        super(Clean, self).__init__(param=param)
        self.addr_field = param.get('addr_field')
        self.company_field = param.get('company_field')

    def get_province(self, cur):
        cur.execute('select name from python_areas WHERE id<=31;')
        result = cur.fetchall()
        province_list = []
        for area in result:
            province_list.append(area[0])
        province_list.sort(key=lambda i: len(i), reverse=True)
        return province_list

    def get_city(self, cur):
        cur.execute('select name from python_areas WHERE id>31;')
        result = cur.fetchall()
        city_list = []
        for city in result:
            city_list.append(city[0])
        city_list.sort(key=lambda i: len(i), reverse=True)
        return city_list

    def parse(self, data_list):
        conn = connect(host='139.196.29.181', port=3306, user='root', password='SuperJoy000',
                       database='pythonsalesmind',
                       charset='utf8')
        cur = conn.cursor()
        city_list = self.get_city(cur)
        province_list = self.get_province(cur)
        for item in data_list:
            sign = ''
            data = json.loads(item['data'])
            if self.sign == 0:
                addr = data.get(self.addr_field)
                company = data.get(self.company_field)
                p = ''
                c = ''
                if addr:
                    for province in province_list:
                        if province in addr:
                            p = province
                            break
                    for city in city_list:
                        if city in addr:
                            c = city
                            break
                    if p or c:
                        if p and p in ['北京', '上海', '天津', '重庆']:
                            c = p
                        elif c:
                            while True:
                                cur.execute('select pid from python_areas where name="{}";'.format(c))
                                result = cur.fetchone()
                                if result[0] <= 31:
                                    break
                                else:
                                    cur.execute('select name from python_areas where id={};'.format(result[0]))
                                    c = cur.fetchone()[0]
                            cur.execute('select name from python_areas where id={};'.format(result[0]))
                            p_ = cur.fetchone()[0]
                            if p == p_:
                                sign = 'True'
                            else:
                                sign = 'False'
                    else:
                        if company:
                            for province in province_list:
                                if province in company:
                                    p = province
                                    break
                            for city in city_list:
                                if city in company:
                                    c = city
                                    break
                            if p and p in ['北京', '上海', '天津', '重庆']:
                                c = p
                            elif c:
                                while True:
                                    cur.execute('select pid from python_areas where name="{}";'.format(c))
                                    result = cur.fetchone()
                                    if result[0] <= 31:
                                        break
                                    else:
                                        cur.execute('select name from python_areas where id={};'.format(result[0]))
                                        c = cur.fetchone()[0]
                                cur.execute('select name from python_areas where id={};'.format(result[0]))
                                p_ = cur.fetchone()[0]
                                if p == p_:
                                    sign = 'True'
                                else:
                                    sign = 'False'
                elif company:
                    for province in province_list:
                        if province in company:
                            p = province
                            break
                    for city in city_list:
                        if city in company:
                            c = city
                            break
                    if p and p in ['北京', '上海', '天津', '重庆']:
                        c = p
                    elif c:
                        while True:
                            cur.execute('select pid from python_areas where name={};'.format(c))
                            result = cur.fetchone()
                            if result[0] <= 31:
                                break
                            else:
                                cur.execute('select name from python_areas where id={};'.format(result[0]))
                                c = cur.fetchone()[0]
                        cur.execute('select name from python_areas where id={};'.format(result[0]))
                        p_ = cur.fetchone()[0]
                        if p == p_:
                            sign = 'True'
                        else:
                            sign = 'False'
                data['省'] = p
                data['市'] = c
                data['result'] = sign
                data['date'] = int(time.time())
                self.col.insert(data)
                self.finish_list.append(item['id'])
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
            # data_list = self.get_data()
            # self.parse(data_list)
            if self.sign == 0:
                SpiderTask.objects.finish_task2(task_id=self.task_id)
                print('{}已完成'.format(self.table_name))
            else:
                print('{}已中断'.format(self.table_name))
        except Exception as E:
            print(E)
            SpiderTask.objects.change_task2_status(task_id=self.task_id)
            print('{}已中断'.format(self.table_name))
