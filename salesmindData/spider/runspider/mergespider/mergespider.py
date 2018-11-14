from spider.models import *
from db.base_spider import BaseSpider
import requests
import threading
from scrapy.selector import Selector
from lxml import etree


class MergeSpider(BaseSpider):
    def __init__(self, param):
        super(MergeSpider, self).__init__(param=param)
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36',
        }

    def parse_zyj(self, data):
        """
        抓取职友集列表
        :param data:
        :return:
        """
        url = 'https://www.jobui.com/cmp?area=全国&keyword={}'.format(data)
        while True:
            try:
                r = requests.get(url, headers=self.headers, proxies=self.get_proxy(), timeout=3)
                break
            except Exception as E:
                # print(E)
                pass
        html = Selector(r)
        company = html.xpath('//ul/li[1]/div[2]/h2/span/a/text()').extract_first(default=' ')
        if data.replace('(', '（').replace(')', '）') == company.replace('(', '（').replace(')', '）'):
            companyid = html.xpath('//ul/li[1]/div[2]//span[@class="admin-companyID"]/text()').extract_first()
            return companyid
        else:
            return None

    def parse_zyj_detail(self, companyid):
        """
        职友集详情
        :param companyid:
        :return:
        """
        detail_url = 'https://www.jobui.com/company/{}/'.format(companyid)
        while True:
            try:
                r = requests.get(detail_url, headers=self.headers, proxies=self.get_proxy(), timeout=3)
                break
            except Exception as E:
                # print(E)
                pass
        html = Selector(r)
        item = {}
        item['公司名称'] = html.xpath('//*[@id="companyH1"]/@data-companyname').extract_first(default=' ')
        item['官方网站'] = html.xpath('//dt[text()="公司网站："]/following-sibling::dd[1]/a/text()').extract_first(default=' ')
        item['公司行业'] = html.xpath('//*[@id="companyH1"]/@data-industrystring').extract_first(default=' ')
        message = html.xpath('//dt[text()="公司信息："]/following-sibling::dd[1]/text()').extract_first()
        if message:
            item['公司性质'] = message.split(' / ')[0].strip()
            try:
                item['公司规模'] = message.split(' / ')[1]
            except:
                item['公司规模'] = ' '
        else:
            item['公司性质'] = ' '
            item['公司规模'] = ' '
        item['公司地址'] = html.xpath('//dt[text()="公司地址："]/following-sibling::dd[1]/text()').extract_first(default=' ')
        item['公司简介'] = ''.join(html.xpath('//*[@id="textShowMore"]//text()').extract())
        item['来源'] = '职友集'
        item['date'] = int(time.time())
        return item

    def parse_51(self, data):
        """
        解析51列表
        :param data:
        :return:
        """
        url = 'https://search.51job.com/list/000000,000000,0000,00,9,99,{},2,1.html?lang=c&stype=1&postchannel=0000&workyear=99&cotype=99&degreefrom=99&jobterm=99&companysize=99&lonlat=0,0&radius=-1&ord_field=0&confirmdate=9&fromType=4&dibiaoid=0&address=&line=&specialarea=00&from=&welfare='
        while True:
            try:
                r = requests.get(url.format(data), headers=self.headers, proxies=self.get_proxy(), timeout=3)
                break
            except Exception as E:
                # print(E)
                pass
        html = etree.HTML(r.content.decode('gbk'))
        company = html.xpath('//*[@id="resultList"]/div[4]/span[1]/a/text()')
        if company:
            if data.replace('(', '（').replace(')', '）') == company[0].replace('(', '（').replace(')', '）'):
                url = html.xpath('//*[@id="resultList"]/div[4]/span[1]/a/@href')[0]
                return url
            else:
                return None

    def parse_51detail(self, url):
        """
        采集详情
        :param url:
        :return:
        """
        while True:
            try:
                r = requests.get(url, headers=self.headers, proxies=self.get_proxy(), timeout=3)
                break
            except Exception as E:
                # print(E)
                pass
        html = etree.HTML(r.content.decode('gbk'))
        item = {}
        try:
            item['公司名称'] = html.xpath('//h1/@title')[0]
        except:
            item['公司名称'] = ' '
        try:
            message = html.xpath('//p[@class="ltype"]/@title')[0]
        except:
            item['公司性质'] = ' '
            item['公司规模'] = ' '
            item['公司行业'] = ' '
            message = ''
        if message:
            item['公司性质'] = message.split('|')[0].replace('\xa0', '')
            try:
                item['公司规模'] = message.split('|')[1].replace('\xa0', '')
            except:
                item['公司规模'] = ' '
            try:
                item['公司行业'] = message.split('|')[2].replace('\xa0', '')
            except:
                item['公司行业'] = ' '
        try:
            item['官方网站'] = html.xpath('//span[text()="公司官网："]/following-sibling::a/text()')[0]
        except:
            item['官方网站'] = ' '
        try:
            item['公司地址'] = ''.join(html.xpath('//span[text()="公司地址："]/../text()')).strip().replace(' ', '')
        except:
            item['公司地址'] = ' '
        try:
            item['公司简介'] = ''.join(html.xpath('//div[@class="con_txt"]//text()')).replace('\r', '').replace('\n',
                                                                                                            '').replace(
                ' ', '')
        except:
            item['公司简介'] = ' '
        item['来源'] = '前程无忧'
        item['date'] = int(time.time())
        return item

    def parse_zhilian(self, data):
        url = 'https://fe-api.zhaopin.com/c/i/sou?pageSize=60&cityId=489&workExperience=-1&education=-1&companyType=-1&employmentType=-1&jobWelfareTag=-1&kw={}&kt=2'.format(
            data)
        while True:
            try:
                r = requests.get(url, headers=self.headers, proxies=self.get_proxy(), timeout=3)
                break
            except Exception as E:
                # print(E)
                pass
        result = json.loads(r.text)
        try:
            company = result['data']['results'][0]['company']['name']
        except:
            return None
        if data.replace('(', '（').replace(')', '）') == company.replace('(', '（').replace(')', '）'):
            detail_url = result['data']['results'][0]['company']['url']
            return detail_url
        else:
            return None

    def parse_zhilian_detail(self, url):
        while True:
            try:
                r = requests.get(url, headers=self.headers, proxies=self.get_proxy(), timeout=3)
                break
            except Exception as E:
                # print(E)
                pass
        html = Selector(r)
        item = {}
        item['公司名称'] = ''.join(html.xpath('//div[@class="mainLeft"]//h1/text()').extract()).strip()
        item['公司性质'] = html.xpath('//span[text()="公司性质："]/../following-sibling::td/span/text()').extract_first(
            default=' ')
        item['公司规模'] = html.xpath('//span[text()="公司规模："]/../following-sibling::td/span/text()').extract_first(
            default=' ')
        item['官方网站'] = html.xpath('//span[text()="公司网站："]/../following-sibling::td/span/a/text()').extract_first(
            default=' ')
        item['公司行业'] = html.xpath('//span[text()="公司行业："]/../following-sibling::td/span/text()').extract_first(
            default=' ')
        item['公司地址'] = html.xpath('//span[text()="公司地址："]/../following-sibling::td/span/text()').extract_first(
            default=' ')
        try:
            info_list = html.xpath('//div[@class="company-content"]//text()').extract()
            info = ''.join(info_list).replace('\r', '').replace('\n', '')
            item['公司简介'] = info
        except Exception as E:
            item['公司简介'] = ' '
        item['来源'] = '智联招聘'
        item['date'] = int(time.time())
        return item

    def run_zyj(self, data_list):
        for data in data_list:
            if self.sign == 0:
                companyid = self.parse_zyj(data['data'])
                if companyid:
                    item = self.parse_zyj_detail(companyid)
                    self.col.insert_one(item)
                self.finish_list.append(data['id'])
            else:
                break

    def run_51(self, data_list):
        for data in data_list:
            if self.sign == 0:
                url = self.parse_51(data['data'])
                if url:
                    item = self.parse_51detail(url)
                    self.col.insert_one(item)
                self.finish_list.append(data['id'])
            else:
                break

    def run_zhilian(self, data_list):
        for data in data_list:
            if self.sign == 0:
                url = self.parse_zhilian(data['data'])
                if url:
                    item = self.parse_zhilian_detail(url)
                    self.col.insert_one(item)
                self.finish_list.append(data['id'])
            else:
                break

    def run(self):
        """
                执行过程
                :return:
                """
        try:
            l = self.get_data()
            cut_list = self.cut_list(l, 10)
            thread_list = []
            for data_list in cut_list:
                t1 = threading.Thread(target=self.run_zyj, args=(data_list,))
                t2 = threading.Thread(target=self.run_51, args=(data_list,))
                t3 = threading.Thread(target=self.run_zhilian, args=(data_list,))
                thread_list.append(t1)
                thread_list.append(t2)
                thread_list.append(t3)
            for t in thread_list:
                t.start()
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
