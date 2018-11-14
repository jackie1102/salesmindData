from lxml import etree
from db.base_spider import *


class ShunQiCondition(BaseSpider):

    def __init__(self, param):
        """
        初始化属性
        """
        super(ShunQiCondition, self).__init__(param=param)
        self.base_url = param.get('base_url')
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36',
        }

    def parse_list(self, url):
        """
        :param url:
        :return:
        """
        while True:
            try:
                result = requests.get(url, headers=self.headers, proxies=self.get_proxy(), timeout=5)
                if result.status_code != 200:
                    continue
                text = result.content.decode()
                html = etree.HTML(text)
                url_list = html.xpath('//ul[@class="companylist"]//h4/a/@href')
                try:
                    next_url = 'http:' + html.xpath('//a[text()="下一页"]/@href')[0]
                except Exception:
                    # print(E)
                    next_url = None
                return [url_list, next_url]
            except requests.RequestException:
                # print(E)
                continue

    def run(self):
        try:
            url = self.base_url
            while True:
                if self.sign == 0:
                    # print(url)
                    temp = self.parse_list(url)
                    url_list = temp[0]
                    SpiderData.objects.add_data_list(data_list=url_list, task_id=self.task_id)
                    url = temp[1]
                    if url:
                        continue
                    else:
                        break
                else:
                    break
            if self.sign == 0:
                SpiderTask.objects.finish_task1(task_id=self.task_id)
                print('{}完成'.format(self.table_name))
            else:
                print('{}已中断'.format(self.table_name))
        except Exception as E:
            print(E)
            SpiderTask.objects.change_task1_status(task_id=self.task_id)
            print('{}已中断'.format(self.table_name))
        self.update_data_count()


class ShunQiConditionParse(BaseSpider):
    def __init__(self, param):
        super(ShunQiConditionParse,self).__init__(param=param)
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36',
        }

    def parse_detail(self, url):
        """
        解析详情页
        :param url:
        :return:
        """
        while True:
            try:
                result = requests.get(url, headers=self.headers, proxies=self.get_proxy(), timeout=5)
                if result.status_code != 200:
                    continue
                text = result.content.decode('utf-8', 'ignore')
                html = etree.HTML(text)
                break
            except requests.RequestException:
                # print(E)
                continue
        item = {}
        try:
            item['爬取公司'] = ''.join(html.xpath('//h1//text()')).replace('\r\n', '')
        except:
            item['爬取公司'] = '-'
        item['公司url'] = result.url
        try:
            info = html.xpath('//*[@id="aboutus"]//div[@class="boxcontent text"]|//*[@id="aboutuscontent"]/span|//*[@id="aboutuscontent"]/span')
            item['公司简介'] = info[0].xpath('string(.)').strip().replace(' ', '').replace('\n', '').replace('\r', '').replace('\t', '')
        except:
            item['公司简介'] = ' '
        try:
            item['公司地址'] = html.xpath('//*[@id="contact"]//dt[text()="公司地址："]/following-sibling::dd[1]/text()')[0]
        except:
            item['公司地址'] = ' '
        try:
            item['固定电话'] = html.xpath('//*[@id="contact"]//dt[text()="固定电话："]/following-sibling::dd[1]/text()')[0]
        except:
            item['固定电话'] = ' '
        try:
            item['经理'] = html.xpath('//*[@id="contact"]//dt[text()="经理："]/following-sibling::dd[1]/text()')[0]
        except:
            item['经理'] = ' '
        try:
            item['手机号码'] = html.xpath('//*[@id="contact"]//dt[text()="手机号码："]/following-sibling::dd[1]/text()')[0]
        except:
            item['手机号码'] = ' '
        try:
            item['电子邮件'] = html.xpath('//*[@id="contact"]//dt[text()="电子邮件："]/following-sibling::dd[1]/text()')[0]
        except:
            item['电子邮件'] = ' '
        try:
            item['经理手机'] = html.xpath('//*[@id="contact"]//dt[text()="经理手机："]/following-sibling::dd[1]/text()')[0]
        except:
            item['经理手机'] = ' '
        try:
            item['职员人数'] = html.xpath('//*[@id="gongshang"]//td[text()="职员人数："]/following-sibling::td[1]/text()')[0]
        except:
            item['职员人数'] = ' '
        item['date'] = int(time.time())
        # print(item)
        return item

    def parse(self, data_list):
        for data in data_list:
            detail = data['data']
            if self.sign == 0:
                if 'http' not in detail:
                    url = 'http:' + detail
                else:
                    url = detail
                item = self.parse_detail(url)
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
