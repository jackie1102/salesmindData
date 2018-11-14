"""
智联招聘参数配置 带有“*”符项 为配置参数
"""
import random
from utils.utils import user_agent_list


# 找到 用户名 密码
username = '17610273593'
password = 'a123456'


# 不可更改
USER_NAME = { 'Iris': 2, 'Lucy': 3, 'Jenny': 4, 'Zora': 5, 'Delia': 6, 'Zachary': 7, 'Jackie': 8, 'Six': 9}

# 用户id , ******不可为空****** 选填：Iris、Lucy、Jenny、Zora、Delia、Zachary、Jackie、Six
USER_ID = 1  # USER_NAME['Delia']

# 下载文件名 ******不可为空******
TABLE_NAME = '早稻测试111'

# ******请求参数 浏览器复制过来******
"""
    寻找方法：登录早稻，跳转条件搜索页面，填写搜索条件，填写完毕，按F12或者右键点击检查，点击搜索，
     在Network中找到 searchPerson 连接点击，然后在右侧 headers 最下方找到 Form data 后面的 view source 点击 然后复制内容。
    """
data_str = 'keyword=%E6%80%BB%E7%BB%8F%E7%90%86&start=0&city=&pageSize=20&YII_CSRF_TOKEN=204f2b9899839d84cc43d397cb7d65fb'

# 爬取列表起始页码  ****** 默认0 第一页 *******
start_page = 0


# 请求头： ******cookie 浏览器复制******

