from lxml import etree
from db.base_spider import *


class ShunQiCompany(BaseSpider):

    def __init__(self, param):
        """
        初始化属性
        :param company_list: 公司列表
        """
        super(ShunQiCompany, self).__init__(param=param)
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36',
        }

    def parse_list(self, company):
        """
        获取搜索公司列表页第一个url
        :param company:
        :return:
        """
        while True:
            try:
                result = requests.get('http://so.11467.com/cse/search?s=662286683871513660&ie=utf-8&q={}'.format(company),
                                      headers=self.headers, proxies=self.get_proxy(), timeout=5)
                text = result.content.decode()
                html = etree.HTML(text)
                break
            except requests.RequestException:
                continue
        node = html.xpath('//div[contains(@class,("result"))]//a/@href')
        company_url = node[0] if len(node) > 0 else None
        return company_url

    def parse_detail(self, url, company):
        """
        解析详情页
        :param url:
        :return:
        """
        while True:
            try:
                result = requests.get(url, headers=self.headers, proxies=self.get_proxy(), timeout=5)
                text = result.content.decode('utf-8', 'ignore')
                html = etree.HTML(text)
                break
            except requests.RequestException:
                continue
        item = {}
        item['列表公司'] = company
        try:
            item['爬取公司'] = ''.join(html.xpath('//h1//text()'))
        except:
            item['爬取公司'] = ' '
        item['公司url'] = result.url
        try:
            info = html.xpath(
                '//*[@id="aboutus"]//div[@class="boxcontent text"]|//*[@id="aboutuscontent"]/span|//*[@id="aboutuscontent"]/span')
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
            company = data['data']
            if self.sign == 0:
                url = self.parse_list(company)
                # print(url)
                if url:
                    item = self.parse_detail(url, company)
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



