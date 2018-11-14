import time
import os
from utils.chaojiying import Chaojiying_Client
from PIL import Image
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from db.base_spider import BaseSpider
from selenium.webdriver.chrome.options import Options


class BASEJOB(BaseSpider):

    def __init__(self, param):
        """
        初始化属性
        :param keywords: str 关键词
        :param any_keywords: bool 是否包含任意关键词
        :param table_name: str 表名
        :param cookies: list cookies
        :param companys: list 公司列表
        :param areas: list 地区列表
        :param content_exp_area: bool 包含期望工作地
        :param exp_areas: list 期望工作地区
        :param position: list 职位列表
        :param only_fun: bool 只搜最近职能
        :param industry: list 行业列表
        :param onlyIndustry: bool 只搜最近行业
        :param work_years: str 工作年限
        :param seaswork: bool 是否有海外经验
        :param education: str 学  历
        :param edu_type: str 学历类型
        :param age: str 年  龄
        :param sex: str 性 别
        :param wages: str 目前月薪
        :param exp_wages: str 期望月薪
        :param major: str 专业
        :param residence: str 户口 用'/' 分开
        :param language: str 语言-水平
        :param englishlevel: str 英语水平
        :param state: str 求职状态
        :param update_time: str 更新时间
        """
        super(BASEJOB, self).__init__(param=param)
        self.page = 1
        self.edu_type = []
        for key in param:
            if 'edu_type' in key:
                self.edu_type.append(param.get(key))
        self.seaswork = param.get('seaswork')
        self.only_fun = param.get('only_fun')
        self.onlyIndustry = param.get('onlyIndustry')
        self.content_exp_area = param.get('content_exp_area')
        self.any_keywords = param.get('any_key')
        self.state = param.get('state')
        self.englishlevel = param.get('englishlevel')
        self.language = param.get('language')
        self.language_level = param.get('language_level')
        self.residence = param.get('residence').split(',') if param.get('residence') else None
        self.major = param.get('major').split(',') if param.get('major') else None
        self.exp_wages = param.get('exp_wages')
        self.wages = param.get('wages')
        self.sex = param.get('sex')
        self.exp_areas = param.get('exp_areas').split(',') if param.get('exp_areas') else None
        self.age = param.get('age')
        self.education = param.get('education')
        self.work_years = param.get('work_years')
        self.industry = param.get('industrys').split(',') if param.get('industrys') else None
        self.keywords = param.get('keywords') if param.get('keywords') else ''  # 修改关键字
        self.vipname = param.get('membername_job51')
        self.username = param.get('username_job51')
        self.password = param.get('password_job51')
        self.areas = param.get('areas').split(',') if param.get('areas') else None  # 地区列表
        self.position = param.get('jobs').split(',') if param.get('jobs') else None
        self.contain_zhijin = param.get('contain_zhijin')
        try:
            self.design_page = int(param.get('design_page'))
        except:
            self.design_page = None
        self.update_time = param.get('update_time') if param.get('update_time') else '近1年'
        chrome_options = Options()
        chrome_options.add_argument('window-size=1920x3000')  # 指定浏览器分辨率
        chrome_options.add_argument('--disable-gpu')  # 谷歌文档提到需要加上这个属性来规避bug
        chrome_options.add_argument('--hide-scrollbars')  # 隐藏滚动条, 应对一些特殊页面
        chrome_options.add_argument('--headless')  # 浏览器不提供可视化页面. linux下如果系统不支持可视化不加这条会启动失败
        self.driver = webdriver.Chrome(chrome_options=chrome_options)
        self.driver.maximize_window()
        self.wait = WebDriverWait(self.driver, 5)

    def search_by_id(self, seard_id):
        id_input = self.wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="ctrlSerach_search_keyword_txt"]')))
        id_input.clear()
        id_input.send_keys(seard_id)
        self.wait.until(
            EC.presence_of_element_located((
                By.XPATH, '//*[@id="ctrlSerach_search_submit"]'))).click()
        time.sleep(1)
        try:
            self.driver.find_element_by_xpath('//span[@class="Common_panel_btn_s"]').click()
        except:
            pass

    # 搜索页面参数配置
    def search_by_ck(self, company_query):
        """
        按公司进行搜索
        :param company_query: 公司名
        :return:
        """
        company_input = self.wait.until(
            EC.presence_of_element_located((
                By.XPATH, '//*[@id="ctrlSerach_search_company_txt"]')))
        company_input.clear()
        company_input.send_keys(company_query)
        self.wait.until(
            EC.presence_of_element_located((
                By.XPATH, '//*[@id="ctrlSerach_search_submit"]'))).click()
        time.sleep(1)

    def search_by_ak(self):
        """
        按关键词进行搜索
        :return:
        """
        self.driver.get('https://ehire.51job.com/Candidate/SearchResumeIndexNew.aspx')
        self.check_yzm()
        self.wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="change_search_term"]'))).click()
        self.wait.until(EC.presence_of_element_located((By.ID, 'search_keywod_txt'))).send_keys(self.keywords)
        self.wait.until(EC.presence_of_element_located((By.ID, 'search_keywod_txt'))).click()
        time.sleep(1)
        self.driver.find_element_by_xpath('//*[@id="search_choose_input"]').click()
        if self.any_keywords == 'on':
            self.wait.until(EC.presence_of_element_located((By.ID, 'search_keyword_anykey'))).click()
        time.sleep(1)
        # 选择地区
        self.wait.until(EC.presence_of_element_located((By.XPATH, '//div[@id="search_area_pare"]/a'))).click()
        try:
            nodes = self.wait.until(
                EC.presence_of_all_elements_located((By.XPATH, '//*[@id="selected_area_div"]/a')))
            if len(nodes) != 0:
                for node in nodes:
                    node.find_element_by_xpath('./i').click()
                    time.sleep(0.5)
        except:
            pass
        self.wait.until(EC.presence_of_element_located((By.LINK_TEXT, '确定'))).click()
        if self.areas:
            for area in self.areas:
                self.wait.until(EC.presence_of_element_located((By.XPATH, '//div[@id="search_area_pare"]/a'))).click()
                if area != '':
                    area_list = area.split('/')
                    time.sleep(1)
                    if len(area_list) == 2:
                        self.wait.until(EC.presence_of_element_located((By.LINK_TEXT, '{}'.format(area_list[0])))).click()
                        self.wait.until(
                            EC.presence_of_element_located((By.XPATH, '//td/a[text()="{}"]'.format(area_list[1])))).click()
                    elif len(area_list) == 3:
                        self.wait.until(EC.presence_of_element_located((By.LINK_TEXT, '{}'.format(area_list[0])))).click()
                        self.wait.until(
                            EC.presence_of_element_located((By.XPATH, '//td/a[text()="{}"]'.format(area_list[1])))).click()
                        node = self.wait.until(
                            EC.presence_of_all_elements_located(
                                (By.XPATH, '//div[@class="Common_subLayer"]')))[1]
                        node.find_element_by_xpath('.//td/a[text()="{}"]'.format(area_list[2])).click()
                self.wait.until(EC.presence_of_element_located((By.LINK_TEXT, '确定'))).click()
            if self.content_exp_area == 'on':
                self.wait.until(
                    EC.presence_of_element_located((
                        By.XPATH, '//*[@id="search_resarea_inexpected"]'))).click()
        # 选择职能
        if self.position and self.position != '':
            for position in self.position:
                if position != '':
                    position_list = position.split('>')
                    self.wait.until(
                        EC.presence_of_element_located((By.XPATH, '//*[@id="search_funtype_pare"]/a'))).click()
                    time.sleep(1)
                    if len(position_list) == 2:
                        self.wait.until(
                            EC.presence_of_element_located((By.XPATH, '//*[@id="EHRDivBoxfun"]//td/p[text()="{}"]'.format(position_list[0])))).click()
                        self.wait.until(
                            EC.presence_of_element_located((By.XPATH, r'//*[@id="EHRSubDivfun"]//td/a[text()="{}"]'.format(position_list[1])))).click()
                    self.wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="EHRDivBoxfun"]/h2/a[1]'))).click()
            if self.only_fun == 'on':
                self.wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="search_onlyFun"]'))).click()
        # 选择行业
        if self.industry and self.industry != '':
            self.wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="search_industry_pare"]/a'))).click()
            for industry in self.industry:
                if industry != '':
                    self.wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="EHRDivBoxind"]//a[text()="{}"]'.format(industry)))).click()
                    time.sleep(0.3)
            self.wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="EHRDivBoxind"]/h2/a[1]'))).click()
            if self.onlyIndustry == 'on':
                self.wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="search_onlyIndustry"]'))).click()
        # 工作年限
        if self.work_years and self.work_years != '':
            work_years_ = self.work_years.split('-')
            self.wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="search_workyearfrom_input"]'))).click()
            self.wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="search_workyearfrom_div"]/a[text()="{}"]'.format(work_years_[0])))).click()
            time.sleep(0.3)
            self.wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="search_workyearto_input"]'))).click()
            self.wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="search_workyearto_div"]/a[text()="{}"]'.format(work_years_[1])))).click()
            if self.seaswork == 'on':
                self.wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="ckboxoverseaswork"]'))).click()
        # 学历
        if self.education:
            education_ = self.education.split('-')
            self.wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="search_degreefrom_input"]'))).click()
            self.wait.until(EC.presence_of_element_located(
                (By.XPATH, '//*[@id="search_workyearfrom_div"]/a[text()="{}"]'.format(education_[0])))).click()
            time.sleep(0.3)
            self.wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="search_degreeto_input"]"]'))).click()
            self.wait.until(EC.presence_of_element_located(
                (By.XPATH, '//*[@id="search_workyearto_div"]/a[text()="{}"]'.format(education_[1])))).click()
        if self.edu_type:
            for edu_type in self.edu_type:
                if edu_type == '985':
                    self.wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="ckbox_985"]'))).click()
                elif edu_type == '211':
                    self.wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="ckbox_211"]'))).click()
                elif edu_type == '全日制':
                    self.wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="ckboxfulltime"]'))).click()
                elif edu_type == '海外留学':
                    self.wait.until(
                        EC.presence_of_element_located((By.XPATH, '//*[@id="ckboxoverseaseducation"]'))).click()
        # 年龄
        if self.age and self.age != '':
            age_ = self.age.split('-')
            self.wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="search_age_from"]'))).send_keys(age_[0])
            self.wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="search_age_to"]'))).send_keys(
                age_[1])
        # 期望工作地区
        if self.exp_areas:
            for item in self.exp_areas:
                if item != '':
                    self.wait.until(
                        EC.presence_of_element_located((By.XPATH, '//*[@id="search_expjobarea_pare"]/a'))).click()
                    time.sleep(0.5)
                    exp_area_list = item.split('/')
                    if len(exp_area_list) == 1:
                        self.wait.until(
                            EC.presence_of_element_located((
                                By.XPATH, '//*[@id="rsm_parentarea_div"]//a[text()="{}"]'.format(exp_area_list[0])))).click()
                    if len(exp_area_list) == 2:
                        self.wait.until(
                            EC.presence_of_element_located((
                                By.XPATH, '//*[@id="rsm_parentarea_div"]//a[text()="{}"]'.format(exp_area_list[0])))).click()
                        self.wait.until(
                            EC.presence_of_element_located(
                                (By.XPATH, '//td/a[text()="{}"]'.format(exp_area_list[1])))).click()
        # 性别
        if self.sex and self.sex != '':
            if self.sex == '男':
                self.wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="man_sex_cn"]'))).click()
            if self.sex == '女':
                self.wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="woman_sex_cn"]'))).click()
            else:
                self.driver.find_element_by_xpath('//*[@id="no_sex_cn"]').click()
        js = "var q=document.documentElement.scrollTop=100000"
        self.driver.execute_script(js)
        # 期望月薪
        if self.exp_wages and self.exp_wages != '':
            exp_wages_ = self.exp_wages.split('-')
            self.wait.until(
                EC.presence_of_element_located((
                    By.XPATH, '//*[@id="search_expectsalaryfrom_input"]'))).click()
            self.wait.until(
                EC.presence_of_element_located((
                    By.XPATH, '//*[@id="search_expectsalaryfrom_div"]/a[text()="{}"]'.format(exp_wages_[0])))).click()
            self.wait.until(
                EC.presence_of_element_located((
                    By.XPATH, '//*[@id="search_expectsalaryto_input"]'))).click()
            self.wait.until(
                EC.presence_of_element_located((
                    By.XPATH, '//*[@id="search_expectsalaryto_div"]/a[text()="{}"]'.format(exp_wages_[1])))).click()
        # 目前月薪
        if self.wages and self.wages != '':
            wages_ = self.wages.split('-')
            self.wait.until(
                EC.presence_of_element_located((
                    By.XPATH, '//*[@id="search_cursalaryfrom_input"]'))).click()
            self.wait.until(
                EC.presence_of_element_located((
                    By.XPATH, '//*[@id="search_cursalaryfrom_div"]/a[text()="{}"]'.format(wages_[0])))).click()
            self.wait.until(
                EC.presence_of_element_located((
                    By.XPATH, '//*[@id="search_cursalaryto_input"]'))).click()
            self.wait.until(
                EC.presence_of_element_located((
                    By.XPATH, '//*[@id="search_cursalaryto_div"]/a[text()="{}"]'.format(wages_[1])))).click()
        # 专业
        if self.major:
            for major in self.major:
                if major != '':
                    major_ = major.split('-')
                    self.wait.until(
                        EC.presence_of_element_located((
                            By.XPATH, '//*[@id="search_major_pare"]/a'))).click()
                    self.wait.until(
                        EC.presence_of_element_located((
                            By.XPATH, '//*[@id="EHRDivBoxmajor"]//td/p[text()="{}"]'.format(major_[0])))).click()
                    self.wait.until(
                        EC.presence_of_element_located((
                            By.XPATH, '//td/a[text()="{}"]'.format(major_[1])))).click()
                    self.wait.until(
                        EC.presence_of_element_located((
                            By.XPATH, '//*[@id="EHRDivBoxmajor"]/h2/a[1]'))).click()
        # 户口
        if self.residence:
            for item in self.residence:
                if item != '':
                    self.wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="search_hukou_pare"]/a'))).click()
                    residence_list = item.split('/')
                    time.sleep(0.5)
                    if len(residence_list) == 1:
                        self.wait.until(
                            EC.presence_of_element_located((
                                By.XPATH, '//*[@id="rsm_parentarea_div"]//p/a[text()="{}"]'.format(residence_list[0])))).click()
                    if len(residence_list) == 2:
                        self.wait.until(
                            EC.presence_of_element_located((
                                By.XPATH, '//*[@id="rsm_parentarea_div"]//p/a[text()="{}"]'.format(residence_list[0])))).click()
                        self.wait.until(
                            EC.presence_of_element_located(
                                (By.XPATH, '//td/a[text()="{}"]'.format(residence_list[1])))).click()
        # 语言
        if self.language and self.language != '不限':
            self.wait.until(
                EC.presence_of_element_located((
                    By.XPATH, '//*[@id="search_dd_forlang_input"]'))).click()
            self.wait.until(
                EC.presence_of_element_located((
                    By.XPATH, '//*[@id="search_dd_forlang_div"]/a[text()="{}"]'.format(self.language)))).click()
            if self.language_level and self.language_level != '':
                self.wait.until(
                    EC.presence_of_element_located((
                        By.XPATH, '//*[@id="search_dd_flevel_input"]'))).click()
                self.wait.until(
                    EC.presence_of_element_located((
                        By.XPATH, '//*[@id="search_dd_flevel_div"]/a[text()="{}"]'.format(self.language_level)))).click()
        # 英语水平
        if self.englishlevel and self.englishlevel != '不限':
            self.wait.until(
                EC.presence_of_element_located((
                    By.XPATH, '//*[@id="search_englishlevel_input"]'))).click()
            self.wait.until(
                EC.presence_of_element_located((
                    By.XPATH, '//*[@id="search_englishlevel_div"]/a[text()="{}"]'.format(self.englishlevel)))).click()
        # 更新时间
        if self.update_time and self.update_time != '':
            self.wait.until(
                EC.presence_of_element_located((
                    By.XPATH, '//*[@id="search_rsmupdate_input"]'))).click()
            self.wait.until(
                EC.presence_of_element_located((
                    By.XPATH, '//*[@id="search_rsmupdate_div"]/a[text()="{}"]'.format(self.update_time)))).click()
        # 求职状态
        if self.state and self.state != '不限':
            self.wait.until(
                EC.presence_of_element_located((
                    By.XPATH, '//*[@id="search_jobstatus_input"]'))).click()
            self.wait.until(
                EC.presence_of_element_located((
                    By.XPATH, '//*[@id="search_jobstatus_div"]/a[text()="{}"]'.format(self.state)))).click()
        self.wait.until(EC.presence_of_element_located((By.ID, 'search_submit'))).click()
        time.sleep(2)
        self.check_yzm()

    def sel_by_method(self, work_time):
        """
        筛选条件
        :param work_time: 工作时间 包含至今
        :return: 标记
        """
        if '至今' in work_time:
            sign = True
        else:
            sign = False
        return sign

    # 监测验证码并作处理
    def check_yzm(self):
        """
         验证码处理：
        1·捕获验证码，对当前页面进行截屏
        2·定位验证码图片位置，并从截屏中提取
        3·调用打码平台，破解验证码，返回验证码参数
        4·对验证码参数进一步处理，并模拟人工操作破解验证码
        5·验证是否破解成功，否则发送验证失败api
        :return:
        """
        while True:
            try:
                imgelement = self.driver.find_element_by_xpath('//*[@id="divValidateHtml"]/div')  # 定位验证码
                self.driver.save_screenshot('aa.png')  # 截取当前网页，该网页有我们需要的验证码
                location = imgelement.location  # 获取验证码x,y轴坐标
                if location['x'] == 0:
                    return
                size = imgelement.size  # 获取验证码的长宽
                rangle = (int(location['x']), int(location['y']), int(location['x'] + size['width']),
                          int(location['y'] + size['height']))  # 写成我们需要截取的位置坐标
                i = Image.open("aa.png")  # 打开截图
                frame4 = i.crop(rangle)  # 使用Image的crop函数，从截图中再次截取我们需要的区域
                frame4.save('frame4.png')
                chaojiying = Chaojiying_Client('jackie1102', 'salesmind1800', '9004')
                im = open('frame4.png', 'rb').read()
                while True:
                    try:
                        res = chaojiying.PostPic(im, 9004)
                    except Exception:
                        time.sleep(2)
                        continue
                    break
                content = res['pic_str'].split('|')
                loc_list = []
                for i in content:
                    loc = i.split(',')
                    loc_list.append(loc)
                action = ActionChains(self.driver)
                for loca in loc_list:
                    action.move_to_element_with_offset(imgelement, int(loca[0]), int(loca[1])).click()
                    action.pause(1)
                action.perform()
                time.sleep(1)
                self.wait.until(EC.presence_of_element_located((By.LINK_TEXT, '验 证'))).click()
                time.sleep(1)
                self.driver.refresh()
                imgelement = self.driver.find_element_by_xpath('//*[@id="divValidateHtml"]/div')  # 定位验证码
                self.driver.save_screenshot('d://aa.png')  # 截取当前网页，该网页有我们需要的验证码
                location = imgelement.location  # 获取验证码x,y轴坐标
                if location['x'] == 0:
                    # print('验证成功')
                    pass
                else:
                    # print('验证失败')
                    chaojiying.ReportError(res['pic_id'])
                time.sleep(3)
            except:
                # print('没有出现验证码')
                break

    # 获取所有详情页 URL
    def parse_list(self):
        """
        解析列表页
        :return: 详情页url列表
        """
        if self.design_page:
            while self.page < self.design_page:
                button = self.wait.until(EC.presence_of_element_located((By.ID, 'pagerBottomNew_nextButton')))
                if button.get_attribute('href'):
                    button.click()
                    time.sleep(1)
                    self.page += 1
                else:
                    break
        url_list = []
        while True:
            print('{}抓取当前页码：{}'.format(self.table_name, self.page))
            self.check_yzm()  # 监测验证码
            try:
                nodes = self.wait.until(
                    EC.presence_of_all_elements_located((By.XPATH, '//tr[contains(@id,"trBaseInfo")]')))
            except:
                break
            for node in nodes:
                try:
                    detail_url = node.find_element_by_xpath(
                        './td[@class="Common_list_table-id-text"]/span/a').get_attribute('href')
                    url_list.append(detail_url)
                except:
                    continue
            time.sleep(1)
            button = self.wait.until(EC.presence_of_all_elements_located((By.XPATH, '//a[@title="下一页"]')))[0]
            if button.get_attribute('href'):
                button.click()
                self.page += 1
            else:
                break
        return url_list

    def login(self):
        self.driver.get('https://ehire.51job.com/')
        time.sleep(1)
        self.wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="txtMemberNameCN"]'))).send_keys(self.vipname)
        self.wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="txtUserNameCN"]'))).send_keys(self.username)
        self.wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="txtPasswordCN"]'))).send_keys(self.password)
        self.wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="btnBeginValidate"]'))).click()
        time.sleep(1)
        while True:
            imgelement = self.driver.find_element_by_xpath('//*[@id="divValidateHtml"]/div')  # 定位验证码
            location = imgelement.location  # 获取验证码x,y轴坐标
            if location['x'] == 0:
                return
            self.driver.save_screenshot('aa.png')  # 截取当前网页，该网页有我们需要的验证码
            size = imgelement.size  # 获取验证码的长宽
            rangle = (int(location['x']), int(location['y']), int(location['x'] + size['width']),
                      int(location['y'] + size['height']))  # 写成我们需要截取的位置坐标
            i = Image.open("aa.png")  # 打开截图
            frame4 = i.crop(rangle)  # 使用Image的crop函数，从截图中再次截取我们需要的区域
            frame4.save('frame4.png')
            chaojiying = Chaojiying_Client('jackie1102', 'salesmind1800', '9004')
            im = open('frame4.png', 'rb').read()
            while True:
                try:
                    res = chaojiying.PostPic(im, 9004)
                except Exception as E:
                    time.sleep(2)
                    continue
                break
            os.remove('aa.png')
            os.remove('frame4.png')
            content = res['pic_str'].split('|')
            loc_list = []
            for i in content:
                loc = i.split(',')
                loc_list.append(loc)
            action = ActionChains(self.driver)
            for loca in loc_list:
                action.move_to_element_with_offset(imgelement, int(loca[0]), int(loca[1])).click()
            action.perform()
            time.sleep(1)
            self.wait.until(EC.presence_of_element_located((By.LINK_TEXT, '验 证'))).click()
            time.sleep(1)
            success = self.driver.find_element_by_xpath('//*[@id="btnEndValidate"]').text
            if success == '验证通过':
                break
            else:
                chaojiying.ReportError(res['pic_id'])
                time.sleep(3)
        self.driver.find_element_by_xpath('//*[@id="Login_btnLoginCN"]').click()

    def parse_detail(self):
        """
        解析详情页
        :return: 数据
        """
        self.check_yzm()
        item = {}
        try:
            item['ID'] = self.driver.find_element_by_xpath('//span[contains(text(), "ID:")]').text.strip().replace(
                'ID:', '')
        except:
            item['ID'] = ' '
        try:
            item['updatetime'] = self.wait.until(
                EC.presence_of_element_located((By.XPATH, '//span[@id="lblResumeUpdateTime"]/b'))).text
        except:
            item['updatetime'] = ' '
        try:
            item['目前状况'] = self.driver.find_element_by_xpath('//table[@class="infr"]//tr[2]/td[1]').text
        except:
            item['目前状况'] = ' '
        try:
            item['到岗时间'] = self.driver.find_element_by_xpath('//td[text()="到岗时间："]/following-sibling::td[1]').text
        except:
            item['到岗时间'] = ' '
        try:
            item['目前薪水'] = self.driver.find_element_by_xpath('//td[contains(text(),"目前年收入")]/span[1]').text.strip()
        except:
            item['目前薪水'] = ' '
        try:
            info = self.driver.find_element_by_xpath('//table[@class="infr"]//tr[3]/td').text
        except:
            info = None
        if info:
            try:
                item['年龄'] = info.split('|')[1].split('（')[0]
            except:
                item['年龄'] = ' '
            try:
                item['现居住地'] = info.split('|')[2].split(' ')[1]
            except:
                item['现居住地'] = ' '
        else:
            item['年龄'] = ' '
            item['现居住地'] = ' '
        node = self.driver.find_element_by_xpath('//td[text()="工作经验"]/../../tr[2]/td/table/tbody/tr[1]')
        try:
            item['company_name'] = node.find_element_by_xpath('.//span[@class="bold"]').text
        except:
            item['company_name'] = ' '
        try:
            item['work_time'] = node.find_element_by_xpath('.//tr[1]/td[@class="time"]').text
        except:
            item['work_time'] = ' '
        try:
            item['work_seniority'] = node.find_element_by_xpath('.//span[@class="gray"]').text.replace(' ', '')
        except:
            item['work_seniority'] = ' '
        try:
            item['position'] = node.find_element_by_xpath('.//td[@class="rtbox"]/strong').text
        except:
            item['position'] = ' '
        try:
            item['industry'] = self.driver.find_element_by_xpath('//td[text()="行　业："]/following-sibling::td').text
        except:
            item['industry'] = ' '
        try:
            item['work_info'] = node.find_element_by_xpath('.//td[text()="工作描述："]/following-sibling::td').text
        except:
            item['work_info'] = ' '
        try:
            item['scale'] = node.find_element_by_xpath('.//span[text()="|"]/..').text.split('|')[1]
        except:
            item['scale'] = ' '
        try:
            item['nature'] = node.find_element_by_xpath('.//span[text()="|"]/..').text.split('|')[2]
        except:
            item['nature'] = ' '
        item['date'] = int(time.time())
        return item