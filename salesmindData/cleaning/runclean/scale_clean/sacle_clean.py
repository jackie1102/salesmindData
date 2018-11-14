from spider.models import *
from db.base_spider import BaseSpider
import re
import copy


class ScaleClean(BaseSpider):
    def __init__(self, param):
        super(ScaleClean, self).__init__(param)
        self.condition_list = param.get('condition').split(' ')
        self.pattern1 = re.compile(r'(\d+-\d+?)人')
        self.pattern2 = re.compile(r'(少于\d+?)人')
        self.pattern3 = re.compile(r'(\d+人以上)')

    def clean1(self, v):
        v_min = int(v.split('-')[0])
        v_max = int(v.split('-')[1])
        v_mid = (v_min+v_max) // 2
        result = None
        for con in self.condition_list:
            if '<' in con:
                if 0< v_mid <= int(con.split('<')[1]):
                    result = con
            if '>' in con:
                if v_mid >= int(con.split('>')[1]):
                    result = con
            if '-' in con:
                if int(con.split('-')[0]) < v_mid < int(con.split('-')[1]):
                    result = con
            if result:
                break
        if result:
            return result
        else:
            return '-'

        # if v_max <= 100:
        #     result = '<100'
        # elif v_max <= 500:
        #     result = '100-500'
        # elif v_max <= 1000:
        #     result = '501-1000'
        # elif v_max <= 5000:
        #     result = '1001-5000'
        # elif v_max <= 10000:
        #     result = '5001-10000'
        # else:
        #     result = '>10000'
        # return result

    def clean2(self, v):
        v = int(v.replace('少于', ''))
        v_mid = v // 2
        result = None
        for con in self.condition_list:
            if '<' in con:
                if 0 < v_mid <= int(con.split('<')[1]):
                    result = con
            elif '>' in con:
                if v_mid >= int(con.split('>')[1]):
                    result = con
            else:
                if int(con.split('-')[0]) < v_mid < int(con.split('-')[1]):
                    result = con
            if result:
                break
        if result:
            return result
        else:
            return '-'
        # if v <= 100:
        #     result = '<100'
        # elif v <= 500:
        #     result = '100-500'
        # elif v <= 1000:
        #     result = '501-1000'
        # elif v <= 5000:
        #     result = '1001-5000'
        # elif v <= 10000:
        #     result = '5001-10000'
        # else:
        #     result = '-'
        # return result

    def clean3(self, v):
        v = int(v.replace('人以上', ''))
        v_mid = v + 10
        result = None
        for con in self.condition_list:
            if '<' in con:
                if 0 < v_mid <= int(con.split('<')[1]):
                    result = con
            elif '>' in con:
                if v_mid >= int(con.split('>')[1]):
                    result = con
            else:
                if int(con.split('-')[0]) < v_mid < int(con.split('-')[1]):
                    result = con
            if result:
                break
        if result:
            return result
        else:
            return '-'
        # if v >= 10000:
        #     result = '>10000'
        # elif v >= 5000:
        #     result = '5001-10000'
        # elif v >= 1000:
        #     result = '1001-5000'
        # elif v >= 500:
        #     result = '500-1000'
        # elif v >= 100:
        #     result = '100-500'
        # else:
        #     result = '<100'
        # return result

    def run(self):
        try:
            for data in self.get_data():
                if self.sign == 0:
                    item = json.loads(copy.copy(data['data']))
                    for key in list(item.keys())[1:]:
                        value = str(item[key])
                        if value:
                            v1 = self.pattern1.findall(value)
                            v2 = self.pattern2.findall(value)
                            v3 = self.pattern3.findall(value)
                            if len(v1) > 0:
                                result = self.clean1(v1[0])
                                item['scale'] = value
                                item['result'] = result
                                item['date'] = int(time.time())
                                self.col.insert_one(item)
                                break
                            elif len(v2) > 0:
                                result = self.clean2(v2[0])
                                item['scale'] = v2[0]
                                item['result'] = result
                                item['date'] = int(time.time())
                                self.col.insert_one(item)
                                break
                            elif len(v3) > 0:
                                result = self.clean3(v3[0])
                                item['scale'] = v3[0]
                                item['result'] = result
                                item['date'] = int(time.time())
                                self.col.insert_one(item)
                                break
                    self.finish_list.append(data['id'])
                else:
                    break
            if self.sign == 0:
                SpiderTask.objects.finish_task2(task_id=self.task_id)
                print('{}人员规模清洗已完成'.format(self.table_name))
            else:
                print('{}人员规模清洗已中断'.format(self.table_name))
        except Exception as E:
            print(str(E))
            SpiderTask.objects.change_task2_status(task_id=self.task_id)
            print('{}人员规模清洗已中断'.format(self.table_name))



