import time
from lxml import etree
import requests
from db.base_spider import BaseSpider


class BASELAGOU(BaseSpider):

    def __init__(self, param):
        super(BASELAGOU, self).__init__(param=param)
        """
        初始化属性
        :param table_name: str 数据库表名
        """
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36',
            'Referer': 'https://www.lagou.com/'
        }

    def parse_detail(self, url):
        """
        解析详情页
        :param url: 详情页url
        :return: item
        """
        item = {}
        while True:
            try:
                r = requests.get(url, headers=self.headers, proxies=self.get_proxy(), timeout=5)
                if 'login' in r.url:
                    continue
                html = etree.HTML(r.content.decode())
                break
            except:
                continue
        company = html.xpath('//div[@class="company_main"]/h1/a/@title')
        item['company'] = company[0] if len(company) > 0 else ' '
        # 网址
        website = html.xpath('//div[@class="company_main"]/h1/a/@href')
        item['website'] = website[0] if len(website) > 0 else ' '
        # 产品列表
        product_list = html.xpath('//div[@class="product_url"]/a[1]/text()')
        item['product'] = ''.join(product_list).replace(' ', '').replace('\n', '') if len(product_list) > 0 else ' '
        # 行业
        industry = html.xpath('//i[@class="type"]/following-sibling::span[1]/text()')
        item['industry'] = industry[0] if len(industry) > 0 else ' '
        # 最新融资时间
        lunci_time = html.xpath('//p[@class="date_year"]/text()')
        item['lunci_time'] = lunci_time[0] if len(lunci_time) > 0 else ' '
        # 轮次
        lunci = html.xpath('//i[@class="process"]/following-sibling::span/text()')
        item['lunci'] = lunci[0] if len(lunci) > 0 else ' '
        # 公司人数
        people_num = html.xpath('//i[@class="number"]/following-sibling::span/text()')
        item['people_num'] = people_num[0] if len(people_num) > 0 else ' '
        # 定位
        addr = html.xpath('//i[@class="address"]/following-sibling::span/text()')
        item['addr'] = addr[0] if len(addr) > 0 else ' '
        # 公司介绍
        company_conten = html.xpath('//span[@class="company_content"]')
        item['company_conten'] = company_conten[0].xpath('string(.)').strip().replace('\n', '') if len(company_conten) > 0 else ' '
        # 公司地址
        address_list = html.xpath('//p[@class="mlist_li_desc"]/text()')
        item['address_list'] = ';'.join(address_list).replace(' ', '').replace('\n', '') if len(address_list) > 0 else ' '
        # 公司LOGO
        img_url = html.xpath('//div[@class="top_info_wrap"]/img/@src')
        item['img_url'] = img_url[0] if len(img_url) > 0 else ' '
        item['date'] = int(time.time())
        return item





