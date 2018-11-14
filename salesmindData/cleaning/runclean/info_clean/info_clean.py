import copy
from threading import Thread

from spider.models import *
from db.base_spider import BaseSpider
from cleaning.runclean.info_clean.conf import area_list


class InfoClean(BaseSpider):
    def __init__(self, param):
        super(InfoClean, self).__init__(param)
        # 筛选字段
        self.company = param.get('company')
        #  公司简介关键词
        self.info_keyword = ['是一家', '致力于', '专注于', '专业从事', '主营业务', '服务商', '提供商', '解决方案', '主要产品', '于一体', '总部']
        # 公司主营关键词
        self.maincamp = ['主要生产', '主要经营', '主营', '主要产品', '主要从事', '是一家', '专注于', '专业从事', '致力于', '提供商', '开发商', '服务商', '解决方案',
                         '为主', '于一体']
        # 知名度关键词
        self.popularity = ['驰名', '知名', '著名', '名牌', '前三', '前十', '十强', '10强', '百强', '100强', '五百强', '500强', '排行榜', '排名',
                           '名列', '十佳', '第三大', '第五大', '第十大', '最大', '最早', '历史最悠久', '最先进', '最具', '创始', '首家', '先驱', '先行者',
                           '领军', '龙头', '领导', '领航', '前列', '领先', '佼佼者', '顶级', '唯一', '独占鳌头', '首屈一指', '一流', '老字号', 'A类企业',
                           '示范', '之王', '之称', '称号']
        self.popularity_ = ['力争为', '将成为', '愿景', '业务涉及', '目前正', '厂房', '装备', '流水线', '目标', '规划', '致力于', '力争', '人才', '生产线',
                            '联合创办', '打造成', '合作', '管理团队', '办公环境', '矢志', '最终发展成为', '最大化', '力争', '合资组建', '知名供应商', '试点',
                            '总公司', '基地', '经验', '坐落', '工厂', '优势', '力争', '逐步', '创始人']
        # 业务分布关键词
        self.business_distribution = ['下属企业', '子公司', '分公司', '办事处', '分支机构', '办事机构', '国家', '省', '自治区', '地区',
                                      '园区', '区域', '东北', '华北', '华东', '华中', '华南', '西南', '长江流域', '珠江流域', '门店', '店铺', '直营店',
                                      '旗舰店', '专卖店', '专营店', '连锁店', '营销中心', '营销服务机构', '运营总部', '运营中心', '研发中心', '销售中心',
                                      '销售代表处', '仓储物流中心', '区域支持中心', '销售办公室', '生产基地', '产业基地', '制造基地', '工厂', '网点', '服务网络',
                                      '销售网络', '遍及', '遍布', '远销', '销往', '参股', '控股', '参控股', '全球', '全国', '海内外', '覆盖', '行销',
                                      '西北', '营销网点', '中国', '蒙古', '朝鲜', '韩国', '日本', '菲律宾', '越南', '老挝', '柬埔寨', '缅甸', '泰国',
                                      '马来西亚', '文莱', '新加坡', '印度尼西亚', '东帝汶', '尼泊尔', '不丹', '孟加拉国', '印度', '巴基斯坦', '斯里兰卡',
                                      '马尔代夫', '哈萨克斯坦', '吉尔吉斯斯坦', '阿富汗', '伊拉克', '伊朗', '叙利亚', '约旦', '黎巴嫩', '以色列', '巴勒斯坦',
                                      '沙特阿拉伯', '巴林', '卡塔尔', '科威特', '阿联酋', '阿曼', '也门', '格鲁吉亚', '亚美尼亚', '阿塞拜疆', '土耳其',
                                      '塞浦路斯', '芬兰', '瑞典', '挪威', '冰岛', '丹麦', '爱沙尼亚', '拉脱维亚', '立陶宛', '俄罗斯', '乌克兰', '摩尔多瓦',
                                      '波兰', '捷克', '斯洛伐克', '匈牙利', '德国', '奥地利', '瑞士', '英国', '爱尔兰', '荷兰', '比利时', '卢森堡',
                                      '法国', '摩纳哥', '罗马尼亚', '保加利亚', '塞尔维亚', '马其顿', '阿尔巴尼亚', '希腊', '斯洛文尼亚', '克罗地亚', '梵蒂冈',
                                      '圣马力诺', '马耳他', '西班牙', '葡萄牙', '安道尔', '埃及', '利比亚', '苏丹', '突尼斯', '阿尔及利亚', '摩洛哥',
                                      '索马里', '吉布提', '肯尼亚', '坦桑尼亚', '乌干达', '卢旺达', '刚果', '几内亚', '尼日尔', '赞比亚', '安哥拉',
                                      '津巴布韦', '马拉维', '马达加斯加', '毛里求斯', '澳大利亚', '新西兰', '巴布亚新几内亚', '所罗门群岛', '帕劳', '瑙鲁',
                                      '图瓦卢', '萨摩亚', '汤加', '加拿大', '美国', '墨西哥', '格陵兰', '危地马拉', '哥斯达黎加', '巴拿马', '巴哈马',
                                      '古巴', '牙买加', '海地', '波多黎各', '哥伦比亚', '委内瑞拉', '苏里南', '厄瓜多尔', '秘鲁', '玻利维亚', '巴西',
                                      '智利', '阿根廷', '乌拉圭', '巴拉圭', '亚洲', '东南亚', '南亚', '西亚', '中亚', '欧洲', '北欧', '中欧', '西欧',
                                      '南欧', '东欧', '中东', '美洲', '北美', '南美', '欧美', '非洲', '东非', '中非', '西非', '南非', '大洋洲']
        # 排除关键词，如果短句中包含关键词就移除
        self.remove_keywords = ['企业文化', '企业理念', '注册资金', '注册资本', '在职人员' '人员规模', '成立', '创建于', '位于', '坐落于', '毗邻', '员工',
                                '雇员', '主要客户', '客户均为', '创始于', '职工']
        # 切割关键词，如果关键词中包含关键词就切除关键词后面的部分
        self.split_keywords = ['福利', '待遇', '邮编', '联系方式', '联系电话', '邮箱', '地址', '法定', '假期', '休假', '节假', '加班', '班车', '员工福利',
                               '五险一金', '公积金']

    # 对各渠道简介进行去重合并
    def merge(self, item):
        str_set = set()
        for key in item.keys():
            if key != self.company:
                data = item[key].replace('.', '。').replace('！', '。').replace('!', '。')
                data_list = data.split('。')
                for d in data_list:
                    for k in self.split_keywords:
                        if k in d:
                            data = data.split(d)[0]
                str_set.add(data)
        str_list = '。'.join(list(str_set))
        data_str = str_list.replace('（', '').replace('）', '').replace('(', '').replace(')', '').replace(' ', '')
        return data_str

    # 原始文本针对公司简介进行切割
    def splitInfo1(self, data):
        data = data.replace('；', '。').replace(';', '。').replace('.', '。').replace('\n', '。').replace('，', ',')
        node1_list = data.split('。')
        return node1_list

    # 原始文本针对其他项切割
    def splitInfo2(self, data):
        data = data.replace('；', ',').replace(';', ',').replace('.', ',').replace('，', ',').replace('。', ',').replace(
            '\n', ',')
        node2_list = data.split(',')
        return node2_list

    # 提取公司简介
    def parseCompanyInfo(self, node_list):
        for nodestr in node_list:
            for key in self.info_keyword:
                if key in nodestr:
                    data = nodestr.replace('\n', '').replace(' ', '')
                    data_list = data.split(',')
                    D_list = copy.copy(data_list)
                    for d in D_list:
                        for k in self.remove_keywords:
                            if k in d:
                                data_list.remove(d)
                                break
                    data_str = ','.join(data_list)
                    return data_str.replace(' ', '')
        else:
            return None

    # 提取公司主营
    def parseMainCamp(self, company_info):
        node_list = company_info.split(',')
        for key in self.maincamp:
            for nodestr in node_list:
                if key in nodestr:
                    if '使命' not in nodestr:
                        return nodestr.replace('\n', '').replace(' ', '')
        else:
            return None

    # 提取公司知名度
    def parsePopularity(self, node_list):
        datastr = []
        copy_list = copy.copy(node_list)
        for nodestr in node_list:
            for key in self.popularity:
                if key in nodestr:
                    copy_list.remove(nodestr)
                    data = nodestr.replace('\n', '').replace(' ', '')
                    data_list = data.split(',')
                    D_list = copy.copy(data_list)
                    for d in D_list:
                        for k in self.remove_keywords:
                            if k in d:
                                data_list.remove(d)
                                break
                    data_str = ','.join(data_list)
                    sign = False
                    for key_ in self.popularity_:
                        if key_ in data_str:
                            sign = True
                            break
                    if not sign:
                        datastr.append(data_str + '；')
                    break
        datastr = ''.join(set(datastr))
        return datastr.replace(' ', ''), copy_list

    # 提取公司业务分布
    def BusinessDistribution(self, node_list, item):
        datastr = []
        self.business_distribution.extend(area_list)
        for nodestr in node_list:
            company = item[self.company].replace('（', '').replace('）', '').replace('(', '').replace(')', '')
            nodestr1 = nodestr.replace(company, '')
            for key in self.business_distribution:
                if key in nodestr1:
                    data = nodestr.replace('\n', '').replace(' ', '')
                    data_list = data.split(',')
                    D_list = copy.copy(data_list)
                    for d in D_list:
                        for k in self.remove_keywords:
                            if k in d:
                                data_list.remove(d)
                                break
                    data_str = ','.join(data_list)
                    datastr.append(data_str + '；')
                    break
        datastr = ''.join(set(datastr))
        return datastr.replace(' ', '')

    def parse(self, data_list):
        for data in data_list:
            if self.sign == 0:
                item = json.loads(data['data'])
                data_str = self.merge(item)
                node_list1 = self.splitInfo1(data_str)
                # 公司简介
                company_info = self.parseCompanyInfo(node_list1)
                node_list2 = self.splitInfo2(data_str)
                # 公司主营
                if company_info:
                    maincamp = self.parseMainCamp(company_info)
                else:
                    maincamp = '-'
                # 公司知名度
                popularity, copy_list = self.parsePopularity(node_list2)
                # 公司业务分布
                businessdistribution = self.BusinessDistribution(copy_list, item)
                item['公司简介_'] = company_info if company_info else '-'
                item['公司主营'] = maincamp if maincamp else '-'
                item['公司知名度'] = popularity if popularity else '-'
                item['公司业务分布'] = businessdistribution if businessdistribution else '-'
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
                print('{}已完成'.format(self.table_name))
            else:
                print('{}已中断'.format(self.table_name))
        except Exception as E:
            print(str(E))
            SpiderTask.objects.change_task2_status(task_id=self.task_id)
            print('{}已中断'.format(self.table_name))
