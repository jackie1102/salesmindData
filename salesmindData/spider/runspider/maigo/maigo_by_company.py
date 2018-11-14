from spider.runspider.maigo.maigo import *


class Maigo_Company(MaiGoParse):
    def __init__(self, param):
        super(Maigo_Company, self).__init__(param=param)

    def parse(self, data_list):
        for data in data_list:
            url = 'http://www.maigoo.com/search/?block=brand&q={}'.format(data['data'])
            while True:
                try:
                    r = requests.get(url, headers=self.headers, proxies=self.get_proxy(), timeout=5)
                    html = Selector(r)
                    break
                except Exception:
                    continue
            url = html.xpath('//div[@class="xgresult"]//ul/li[1]/a/@href').extract_first()
            if self.sign == 0:
                item = self.parse_detail(url, data['data'])
                self.col.insert(item)
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
            print(E)
            SpiderTask.objects.change_task2_status(task_id=self.task_id)
            print('{}已中断'.format(self.table_name))


