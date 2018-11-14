import json
import requests
from db.base_spider import BaseSpider


class BaseZhaoPin(BaseSpider):
    """
    连接数据库
    """
    def __init__(self, param):
        """
        初始化属性
        """
        super(BaseZhaoPin,self).__init__(param=param)
        self.headers = {
            'Cookie': param.get('login_cookie'),
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'
        }

    def get_access_token(self):
        # 获取access_token
        auth_url = 'http://ihr.zhaopin.com/api/user/authLogin.do'
        response = requests.get(url=auth_url, headers=self.headers)
        a = response.text
        a = json.loads(a)
        access_token = a['data']['token']
        return access_token









