import random
from pymongo import MongoClient
from utils.utils import user_agent_list
"""
    配置文件，请详细看每一个配置 “*” 为配置项
"""


# 从浏览器获取 ******cookie****** 粘贴到 headers
headers = {
    'Cookie': '_user_identify_=af8538f6-f0cf-3147-86d7-f38c4d47c504; JSESSIONID=aaaLoHLzcsaxxgYnJsCnw; Hm_lvt_37854ae85b75cf05012d4d71db2a355a=1526261750; Hm_lvt_ddf0d99bc06024e29662071b7fc5044f=1526261750; uID=461344; sID=563267283fa0051aef97aa8805b2f303; Hm_lpvt_ddf0d99bc06024e29662071b7fc5044f=1526261779; Hm_lpvt_37854ae85b75cf05012d4d71db2a355a=1526261779',
    'User-Agent': random.choice(user_agent_list)
}

# ******页码配置******  1 为第一页
start = 1   # 起始页码
end = 10    # 终止页码

# 用户名 不可更改
USER_NAME = {'Iris': 2, 'Lucy': 3, 'Jenny': 4, 'Zora': 5, 'Delia': 6, 'Zachary': 7, 'Jackie': 8, 'Six': 9}

# 用户id , ******不可为空****** 选填：Iris、Lucy、Jenny、Zora、Delia、Zachary、Jackie、Six
USER_ID = USER_NAME['Jackie']

# 爬虫名/下载文件名 ******不可为空******
table_name = ''

# 不可更改
lunci = {'3': 'pre_A', '4': 'A', '5': 'A+', '6': 'pre_B', '7': 'B', '8': 'B+', '10': 'C', '11': 'C+', '13': 'D', '15': 'E', '16': 'F', '17': 'G'}


# 连接数据库 不可更改
client = MongoClient(host="139.196.29.181", port=27017)
db = client['salesmindSpider']
db.authenticate("spider1", "123456")
col = db[table_name]

