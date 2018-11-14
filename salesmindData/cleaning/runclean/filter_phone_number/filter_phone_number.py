import re
from spider.models import *
from db.base_spider import BaseSpider


class FILTERPHONE(BaseSpider):

    def __init__(self, param):
        """
        初始化属性
        :param param:
        :param data_list:
        """
        super(FILTERPHONE, self).__init__(param=param)
        self.no_phone = param.get('no_phone')
        self.field = param.get('field')

    def run(self):
        """
        执行过程
        :return:
        """
        try:
            for item in self.get_data():
                data = json.loads(item['data'])
                # if self.sign == 0:
                #     phonenumber = str(data.get(self.field)).split('.')[0]
                #     if self.no_phone == 'on':
                #         if not re.search(r'^1([358][0-9]|4[579]|66|7[0135678]|9[89])[0-9]{8}$', phonenumber):
                #             data['date'] = int(time.time())
                #             self.col.insert_one(data)
                #     else:
                #         if re.search(r'^1([358][0-9]|4[579]|66|7[0135678]|9[89])[0-9]{8}$', phonenumber):
                #             data['date'] = int(time.time())
                #             self.col.insert_one(data)
                #     self.finish_list.append(item['id'])
                # else:
                #     break
                if self.sign == 0:
                    phonenumber = str(data.get(self.field)).split('.')[0]
                    if self.no_phone == 'on':
                        if not re.search(r'^1([358][0-9]|4[579]|66|7[0135678]|9[89])[0-9]{8}$', phonenumber):
                            data['date'] = int(time.time())
                            self.col.insert_one(data)
                    else:
                        phone_list = re.findall(r'(1([358][0-9]|4[579]|66|7[0135678]|9[89])[0-9]{8})', phonenumber)
                        if phone_list:
                            phone_ = ''
                            for phone in phone_list:
                                phone_ += phone[0] + '；'
                            data['手机号_新'] = phone_
                            data['date'] = int(time.time())
                            self.col.insert_one(data)
                    self.finish_list.append(item['id'])
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

