import time
from spider.runspider.zdao.CK import CrackGeetest
from pymongo import MongoClient
from utils.update import update_task_state
import logging
logger = logging.getLogger('django')


class BASEZAODAO(CrackGeetest):
    """
    继承父类：CrackGeetest
    """
    def __init__(self, table_name, username, password):
        """
        初始化属性
        :param conditions: list 条件参数 ['省份'，'市区'，'关键词']
        :param table_name: str 表名
        :param cookies: list COOKIE值
        """
        super(BASEZAODAO, self).__init__()
        self.username = username
        self.password = password
        self.table_name = table_name
        client = MongoClient(host="139.196.29.181", port=27017)
        db = client['salesmindSpider']
        db.authenticate("spider1", "123456")
        self.col = db[self.table_name]
        self.driver.maximize_window()

    def check_YZM(self):
        """
        检测并处理验证码
        :return:
        """
        self.driver.find_element_by_id('geetest_dialog')
        self.crack()

    def update_task(self):
        """
        更新任务状态，退出浏览器
        :return:
        """
        print('{}爬取完成'.format(self.table_name))
        logger.info('早稻爬取完成')

    def login(self):
        # 请求起始url
        self.driver.get('https://www.zdao.com/user/login')
        time.sleep(2)
        try:
            self.check_YZM()
        except:
            pass
        time.sleep(1)
        self.driver.find_element_by_xpath('//div[@class="normal_tab tab_account"]').click()
        self.driver.find_element_by_xpath('//div[@class="login_by_account"]/div[1]/input').send_keys(self.username)
        time.sleep(0.5)
        self.driver.find_element_by_xpath('//div[@class="login_by_account"]/div[2]/input').send_keys(self.password)
        time.sleep(0.5)
        self.driver.find_element_by_xpath('//div[@class="login_by_account"]/div[4]').click()
        # 设置等待时间输入关键字 点击搜索
        time.sleep(1)
        try:
            self.check_YZM()
        except:
            pass
        time.sleep(3)
        cookie = [item["name"] + "=" + item["value"] for item in self.driver.get_cookies()]
        cookiestr = ';'.join(item for item in cookie)
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36',
            'Host': 'www.zdao.com',
            'X-Requested-With': 'XMLHttpRequest',
            'Origin': 'https://www.zdao.com',
            'Cookie': cookiestr
        }



