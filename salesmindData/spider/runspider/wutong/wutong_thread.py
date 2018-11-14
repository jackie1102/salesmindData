import re
from threading import Thread

import requests
from PIL import Image
from lxml import etree
from db.base_spider import BaseSpider
from spider.models import *
from aip import AipOcr
import os


class WuTong(BaseSpider):
    def __init__(self, param):
        super(WuTong, self).__init__(param=param)
        self.totle_page = param.get('totle_page')
        self.base_url = param.get('base_url') + 'page{}'
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.108 Safari/537.36',
        }

    def parse(self, url):
        while True:
            try:
                r = requests.get(url, headers=self.headers, proxies=self.get_proxy(),timeout=5)
                html = etree.HTML(r.content.decode('gbk', 'ignore'))
                break
            except:
                continue
        items = []
        nodes = html.xpath('//ul[@class="qiYeKuList"]/li')
        for i in nodes:
            item = {}
            company_name = i.xpath('.//a[contains(@class,"qiYeName")]/text()')
            item['company_name'] = ''.join(str(_).strip() for _ in company_name)
            href = i.xpath('.//a[contains(@class,"qiYeName")]/@href')
            item['href'] = ''.join(str(_).strip() for _ in href)
            location = i.xpath('.//div[contains(@class,"location")]/text()')
            item['location'] = ''.join(str(i).strip() for i in location)
            detail = i.xpath('.//p/text()')
            item['detail'] = ''.join(str(i).strip() for i in detail)
            items.append(json.dumps(item))
        return items

    def run(self):
        try:
            for page in range(1, int(self.totle_page)+1):
                if self.sign == 0:
                    print('{}当前抓取页码：{}'.format(self.table_name, page))
                    url = self.base_url.format(page)
                    url_list = self.parse(url)
                    SpiderData.objects.add_data_list(url_list,task_id=self.task_id)
                else:
                    break
            if self.sign == 0:
                SpiderTask.objects.finish_task1(task_id=self.task_id)
                print('{}url采集已完成'.format(self.table_name))
            else:
                print('{}url采集已中断'.format(self.table_name))
        except Exception as E:
            print(str(E))
            SpiderTask.objects.change_task1_status(task_id=self.task_id)
            print('{}url采集已中断'.format(self.table_name))
        finally:
            self.update_data_count()


class WuTongParse(BaseSpider):
    def __init__(self,param):
        super(WuTongParse, self).__init__(param)
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.108 Safari/537.36',
        }

    def parse_detail(self, url, item):
        while True:
            try:
                r = requests.get(url, headers=self.headers, proxies=self.get_proxy(), timeout=5)
                html = etree.HTML(r.content.decode('gbk', 'ignore'))
                break
            except:
                continue
        try:
            detail = ''.join(html.xpath('//*[@id="ctl00_cph_WLmaster_CompDesc1_dvDesc"]//text()')).replace(' ', '')
            if detail:
                item['DETAIL'] = detail
            else:
                detail = ''.join(html.xpath('//*[@id="divJj"]/div/div[1]//text()')).replace(' ', '')
                item['DETAIL'] = detail
        except:
            detail = '-'
        try:
            item['联系人'] = re.findall(r'服务热线：<br />(.*?)<br',r.text, re.S)[0].strip()
        except Exception as E:
            item['联系人'] = '-'
        try:
            item['phone'] = ''
            img_urls = html.xpath('//span[@class="ContactUsNum"]/img/@src')
            if img_urls:
                for img_url in img_urls:
                    phone = self.imgtostr(img_url,referer_url=url)
                    item['phone'] += phone + ';'
            else:
                img_url = html.xpath('//li[2]/img/@src')[0]
                item['phone'] = self.imgtostr(img_url,referer_url=url)
        except Exception as E:
            item['phone'] = '-'
        return item

    def get_file_content(self,path):
        with open(path, 'rb') as fp:
            return fp.read()

    def imgtostr(self,img_url,referer_url):
        APP_ID = '11444746'
        API_KEY = 'UGvLDGzTOmI3HW1QNGLQ85Pv'
        SECRET_KEY = 'u7B9qwng8Efi8XDZAl9YIumqVve26NeA'
        headers = self.headers
        headers['Referer'] = referer_url
        r = requests.get(img_url,headers=headers)
        with open('phone.jpg', 'wb') as F:
            F.write(r.content)
        im = Image.open('phone.jpg')
        im = im.convert('RGB')
        im.save('phone.jpg')
        img = self.get_file_content('phone.jpg')
        client = AipOcr(APP_ID, API_KEY, SECRET_KEY)
        #  调用通用文字识别, 图片参数为本地图片
        result = client.basicAccurate(img)
        phone = result['words_result'][0]['words']
        os.remove('phone.jpg')
        return phone

    def run(self):
        try:
            for data in self.get_data():
                if self.sign == 0:
                    item = json.loads(data['data'])
                    url = item['href']
                    item = self.parse_detail(url, item)
                    item['date'] = int(time.time())
                    self.col.insert_one(item)
                    self.finish_list.append(data['id'])
                else:
                    break
            if self.sign == 0:
                print('{}采集详情已完成'.format(self.table_name))
                SpiderTask.objects.finish_task2(task_id=self.task_id)
            else:
                print('{}采集详情已中断'.format(self.table_name))
        except Exception as E:
            print(str(E))
            SpiderTask.objects.change_task2_status(task_id=self.task_id)
            print('{}采集详情已中断'.format(self.table_name))


class WuTongCompany(BaseSpider):
    def __init__(self, param):
        super(WuTongCompany, self).__init__(param)
        self.base_url = param.get('base_url').split('/m')[0] + '/m{}ft/'
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.108 Safari/537.36',
        }

    def parse_list(self, data):
        for i in range(5):
            try:
                r = requests.get(self.base_url.format(data), headers=self.headers, proxies=self.get_proxy(),timeout=5)
                html = etree.HTML(r.content.decode('gbk', 'ignore'))
                break
            except:
                continue
        else:
            return None
        if not html:
            return None
        item = {}
        company_name = html.xpath('//ul[@class="qiYeKuList"]/li[1]//a[contains(@class,"qiYeName")]/text()')
        item['company_name'] = ''.join(str(_).strip() for _ in company_name)
        href = html.xpath('//ul[@class="qiYeKuList"]/li[1]//a[contains(@class,"qiYeName")]/@href')
        item['href'] = ''.join(str(_).strip() for _ in href)
        location = html.xpath('//ul[@class="qiYeKuList"]/li[1]//div[contains(@class,"location")]/text()')
        item['location'] = ''.join(str(i).strip() for i in location)
        detail = html.xpath('//ul[@class="qiYeKuList"]/li[1]//p/text()')
        item['detail'] = ''.join(str(i).strip() for i in detail)
        return item

    def parse_detail(self, item):
        url = item['href']
        for i in range(5):
            try:
                r = requests.get(url, headers=self.headers, proxies=self.get_proxy(),timeout=5)
                html = etree.HTML(r.content.decode('gbk', 'ignore'))
                break
            except:
                continue
        else:
            return None
        try:
            item['联系人'] = re.findall(r'服务热线：<br />(.*?)<br',r.text, re.S)[0].strip()
        except Exception as E:
            item['联系人'] = '-'
        try:
            item['phone'] = ''
            img_urls = html.xpath('//span[@class="ContactUsNum"]/img/@src')
            if img_urls:
                for img_url in img_urls:
                    phone = self.imgtostr(img_url,referer_url=url)
                    item['phone'] += phone + ';'
            else:
                img_url = html.xpath('//li[2]/img/@src')[0]
                item['phone'] = self.imgtostr(img_url,referer_url=url)
        except Exception as E:
            item['phone'] = '-'
        return item

    def get_file_content(self,path):
        with open(path, 'rb') as fp:
            return fp.read()

    def imgtostr(self,img_url,referer_url):
        APP_ID = '11444746'
        API_KEY = 'UGvLDGzTOmI3HW1QNGLQ85Pv'
        SECRET_KEY = 'u7B9qwng8Efi8XDZAl9YIumqVve26NeA'
        headers = self.headers
        headers['Referer'] = referer_url
        r = requests.get(img_url,headers=headers)
        with open('phone.jpg', 'wb') as F:
            F.write(r.content)
        im = Image.open('phone.jpg')
        im = im.convert('RGB')
        im.save('phone.jpg')
        img = self.get_file_content('phone.jpg')
        client = AipOcr(APP_ID, API_KEY, SECRET_KEY)
        #  调用通用文字识别, 图片参数为本地图片
        result = client.basicAccurate(img)
        phone = result['words_result'][0]['words']
        os.remove('phone.jpg')
        return phone

    def parse(self, data_list):
        for data in data_list:
            if self.sign == 0:
                item = self.parse_list(data['data'])
                if item:
                    item = self.parse_detail(item)
                if item:
                    item['date'] = int(time.time())
                    self.col.insert_one(item)
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
                print('{}详情采集已完成'.format(self.table_name))
            else:
                print('{}详情采集已中断'.format(self.table_name))
        except Exception as E:
            print(str(E))
            SpiderTask.objects.change_task2_status(task_id=self.task_id)
            print('{}详情采集已中断'.format(self.table_name))
