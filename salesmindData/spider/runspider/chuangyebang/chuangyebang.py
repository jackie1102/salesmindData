import re
import requests
from lxml import html
from spider.models import *
from db.base_spider import BaseSpider

# 修改链接
cookie = {
    'Cookie': 'BAIDU_SSP_lcr=https://www.google.com.hk/; __utma=22723113.1992140974.1496203791.1496213503.1496220940.3; __utmc=22723113; __utmz=22723113.1496220940.3.3.utmcsr=google|utmccn=(organic)|utmcmd=organic|utmctr=(not%20provided); __utmv=22723113.|1=user=null_null=1; Hm_lvt_5f6b02d88ea6aa37bfd72ee1b554bf6f=1496203790,1496213503,1496220940; Hm_lpvt_5f6b02d88ea6aa37bfd72ee1b554bf6f=1496221033'}
header = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
          'Accept-Encoding': 'gzip, deflate, sdch', 'Accept-Language': 'zh-CN,zh;q=0.8',
          'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'}


class Chuangyebang(BaseSpider):
    def __init__(self, param):
        super(Chuangyebang, self).__init__(param=param)
        self.BASE_URL = 'http://wwv.cyzone.cn/event/list-764-0-{}-2-0-0-0/'

    def generate_page(self):
        yield from range(1, 890)

    def parse_page(self, url):
        session = requests.session()
        response = session.get(url=url, headers=header, cookies=cookie).text
        sel = html.fromstring(response)
        items = sel.xpath('//tr[@class="table-plate3"]')
        companys = []
        for _ in items:
            item = {}
            investors = _.xpath('td[@class="tp3"]/@title')[0]
            item['investor'] = re.sub(r'[\t\r\n,]', '', investors).replace(' ', '')
            item['product_name'] = _.xpath('td[@class="tp2"]/span[@class="tp2_tit"]/a/text()')[0]
            item['company'] = ''.join([str(i) for i in _.xpath('td[@class="tp2"]/span[@class="tp2_com"]/text()')])
            item['financial_amount'] = ''.join(str(i) for i in _.xpath('td[3]/div[@class="money"]/text()'))
            item['rounds'] = ''.join(str(i) for i in _.xpath('td[4]/text()'))
            item['industry'] = ''.join(str(i) for i in _.xpath('td[last()-2]/a/text()'))
            item['times'] = ''.join(str(i) for i in _.xpath('td[last()-1]/text()'))
            item['image_path'] = _.xpath('td[1]/a/img/@src')[0]
            print(item)
            companys.append(item)
        return companys

    def run(self):
        g = self.generate_page()
        while True:
            try:
                page_num = g.send(None)
                url = self.BASE_URL.format(page_num)
                print(url)
                companys = self.parse_page(url)
                print(companys)
                self.col.insert_many(companys)
                time.sleep(20)
            except StopIteration:
                break
            finally:
                SpiderTask.objects.finish_task1(task_id=self.task_id)
