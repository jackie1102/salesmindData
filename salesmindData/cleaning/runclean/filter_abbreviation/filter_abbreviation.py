from pymysql import connect
from cleaning.runclean.filter_abbreviation.data import *
from spider.models import *
from db.base_spider import BaseSpider


class FILTEABBREVIATION(BaseSpider):

    def __init__(self, param):
        """
        初始化属性
        :param param: dict 表单数据
        :param data_list: 上传文件数据
        """
        super(FILTEABBREVIATION, self).__init__(param=param)
        self.field = param.get('field')
        self.conn = connect(host='139.196.29.181', port=3306, user='root', password='SuperJoy000', database='pythonsalesmind',
                            charset='utf8')
        self.cur = self.conn.cursor()
        self.cur.execute('select name from python_areas;')
        self.result = self.cur.fetchall()

    def filter_(self):
        """
        过滤去除简称以外的字段以及省市
        :return:
        """
        for item in self.get_data():
            data = json.loads(item['data'])
            if self.sign == 0:
                value = data.get(self.field)
                for sel in data_list:
                    value = value.split(sel)[0]
                for replace_item in replace_list:
                    value = value.replace(replace_item, '')
                area_list = []
                for area in self.result:
                    area_list.append(area[0])
                area_list.sort(key=lambda i: len(i), reverse=True)
                for area in area_list:
                    value = value.replace(area, '')
                data['简称'] = value
                data['date'] = int(time.time())
                self.col.insert_one(data)
                self.finish_list.append(item['id'])
            else:
                break

    def run(self):
        """
        执行过程
        :return:
        """
        try:
            self.filter_()
            if self.sign == 0:
                SpiderTask.objects.finish_task2(task_id=self.task_id)
                print('{}已完成'.format(self.table_name))
            else:
                print('{}已中断'.format(self.table_name))
        except Exception as E:
            print(E)
            SpiderTask.objects.change_task2_status(task_id=self.task_id)
            print('{}已中断'.format(self.table_name))