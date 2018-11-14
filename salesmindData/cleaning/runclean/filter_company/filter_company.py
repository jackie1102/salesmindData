from spider.models import *
from db.base_spider import BaseSpider


class FILTERCOMPANY(BaseSpider):

    def __init__(self, param):
        """
        初始化属性
        :param keywords: 公司中包含的关键词
        :param data_list: 数据列表
        :param tanble_name: 数据库表名
        """
        super(FILTERCOMPANY, self).__init__(param=param)
        num = param.get('number')
        condition_list = []
        for i in range(int(num)):
            item = {}
            keywords = 'keywords{}'.format(i)
            col = 'col{}'.format(i)
            contain_keyword = 'contain_keyword{}'.format(i)
            item['keywords'] = param.get(keywords)
            item['col'] = param.get(col)
            item['contain_keyword'] = param.get(contain_keyword)
            condition_list.append(item)
        self.condition_list = condition_list

    def run(self):
        """
        执行过程
        :return:
        """
        try:
            for item in self.get_data():
                data = json.loads(item['data'])
                if self.sign == 0:
                    sign = False
                    for condition in self.condition_list:
                        contain_keyword = condition.get('contain_keyword')
                        keywords = condition.get('keywords').split(' ')
                        index = condition.get('col')
                        # 筛选包含关键词的公司
                        if contain_keyword == 'on':
                            sign = False
                            for keyword in keywords:
                                if keyword and keyword.upper() in str(data[index]).upper():
                                    sign = True
                                    break
                            if not sign:
                                break
                        # 筛选不包含关键词的公司
                        if not contain_keyword:
                            sign = False
                            for keyword in keywords:
                                if keyword and keyword.upper() not in str(data[index]).upper():
                                    sign = True
                                else:
                                    sign = False
                                    break
                            if not sign:
                                break
                    if sign:
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