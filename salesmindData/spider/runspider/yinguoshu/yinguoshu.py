import time
import requests
import json
from spider.runspider.yinguoshu.conf import *
from utils.update import update_task_state
from spider.models import save_task
import threading


def get_proxy():
    """
    获取IP代理
    :return:
    """
    res = requests.get(
        'http://101.132.104.154:10000/get_proxy')
    content = res.content.decode()
    # print(content)
    ipdict = json.loads(content)
    ip_list = ipdict.get('ip_list')
    ip_address = random.choice(ip_list)
    proxy = {
        'http': ip_address,
        'https': ip_address,
    }
    return proxy


def parse_():
    """
    获取列表页内容
    :return:
    """
    for i in range(start, end + 1):
        while True:
            try:
                r = requests.get('https://www.innotree.cn/inno/search/ajax/getAllSearchResult?query=&tagquery=&st={}&ps=10&areaName=&rounds=&show=0&idate=&edate=&cSEdate=-1&cSRound=-1&cSFdate=1&cSInum=-1&iSNInum=1&iSInum=-1&iSEnum=-1&iSEdate=-1&fchain='.format(i),
                                 headers=headers, proxies=get_proxy(), timeout=5)
                content = r.text
                print(content)
                data_dict = json.loads(content)
                break
            except Exception as E:
                print(E)
                time.sleep(3)
                continue
        print(i)
        yield data_dict


def parse_detail():
    """
    提取数据
    :return:
    """
    for data in parse_():
        nodes = data['data']['company']['infos']
        for node in nodes:
            item = {}
            item['公司名'] = node['name']
            item['公司简称'] = node['alias']
            item['标签'] = node['tags']
            item['融资时间'] = node['idate']
            item['融资金额'] = node['amount']
            item['当前轮次'] = lunci.get(str(node['round']))
            item['所在地'] = node['address']
            item['成立时间'] = node['edate']
            print(item)
            col.insert(item)
        time.sleep(3)
    update_task_state(table_name)
    print('{}爬取完成'.format(table_name))


if __name__ == '__main__':
    T = threading.Thread(target=parse_detail)
    T.start()
    save_task(table_name, USER_ID)