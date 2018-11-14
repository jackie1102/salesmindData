from spider.runspider.zhaopin_ import zhilian_condition_parse_, zhaopin_condition_, zhaopin_company_
from spider.runspider.zhaopin import zhaopin_ID, zhiliandownByID, zhaopin_company, zhaopin_condition, zhilian_condition_parse
from spider.runspider.atubo import spider_atubo_impl
from spider.runspider.shunqi import shunqi, shunqi_condition
from spider.runspider.liepin import liepin_by_condition, liepin_by_ID_company, liepinDownByID
from spider.runspider.baidubaipin import baidubp, baidubp_company
from spider.runspider.boss import boss_company, boss_position
from spider.runspider.ganji import ganji_condition, ganji_by_company
from spider.runspider.mergespider import mergespider
from spider.runspider.jincheng import jinchengSpider
from spider.runspider.kanzhunwang import kanzhun
from spider.runspider.lagou import spider_lagou_impl
from spider.runspider.liepin_prev import liepin_prev, liepin_prev_company
from spider.runspider.maigo import maigo, maigo_by_company
from spider.runspider.qymgc import qymgc
from spider.runspider.sole import sole
from spider.runspider.recruit_51 import recruit_51_thread
from spider.runspider.zhaopin51_baidu import zhaopin51
from cleaning.runclean.query_phone import query_phone
from cleaning.runclean.filter_phone_number import filter_phone_number
from cleaning.runclean.extract_city import extract_city
from cleaning.runclean.filter_abbreviation import filter_abbreviation
from cleaning.runclean.filter_company import filter_company
from cleaning.runclean.scale_clean import sacle_clean
from spider.runspider.job51 import spider_job_impl, job51downByID
from spider.runspider.job51_ import job51_, job51_company
from spider.runspider.qichacha import qichacha
from spider.runspider.tianyancha import tianyancha
from spider.runspider.zhiyouji import zhiyouji
from spider.runspider.baidu import asyncio_baidu
from spider.runspider.wutong import wutong_thread
from cleaning.runclean.info_clean import info_clean,info_contain
from cleaning.runclean.match_company import match_company
from spider.runspider.zhilian_recruit import recruit_thread
from spider.runspider.qichacha_ import qichacha_


TaskCode1 = {
    "a0": zhaopin_condition_.ZhaoPin,
    "0" : zhaopin_condition.ZhaoPin,
    "2": spider_atubo_impl.ConditionAtuBo,
    "4": shunqi_condition.ShunQiCondition,
    "6": liepin_by_condition.LiePinCondition,
    "8": baidubp.BaiduBaipin,
    "10": boss_position.Spider,
    "12": ganji_condition.Spider,
    "14": jinchengSpider.Jincheng,
    "16": spider_lagou_impl.LAGOU,
    "18": liepin_prev.Spider,
    "20": maigo.MaiGo,
    "22": recruit_51_thread.Recruit_51,
    "a24": job51_.JobAk,
    "24": spider_job_impl.JOBAK,
    "26": wutong_thread.WuTong,
    "28": recruit_thread.ZhilianRecruit,
}

TaskCode2 = {
    "a0": zhilian_condition_parse_.ZhaoPinParse,
    "a1": zhaopin_company_.ZhaoPin_Company,
    "0": zhilian_condition_parse.ZhaoPinParse,
    "1": zhaopin_company.ZhaoPin_Company,
    "2": spider_atubo_impl.ConditionAtuBoParse,
    "3": zhaopin_ID.ZhaoPin_ID,
    "4": shunqi_condition.ShunQiConditionParse,
    "5": spider_atubo_impl.ATUBO,
    "6": liepin_by_condition.LiePinConditionParse,
    "7": shunqi.ShunQiCompany,
    "8": baidubp.BaiDuBaiPinParse,
    "9": liepin_by_ID_company.LiePinIdCompany,
    "10": boss_position.SpiderParse,
    "11": baidubp_company.BaiduBaipin,
    "12": ganji_condition.SpiderParse,
    "13": boss_company.Spider,
    "14": jinchengSpider.JinChenParse,
    "15": ganji_by_company.Spider,
    "16": spider_lagou_impl.LaGouParse,
    "17": mergespider.MergeSpider,
    "18": liepin_prev.LiePinParse,
    "19": kanzhun.Spider,
    "20": maigo.MaiGoParse,
    "21": spider_lagou_impl.LAGOU_COMPANY,
    "22": recruit_51_thread.Recruit_51_Parse,
    "23": liepin_prev_company.Spider,
    "a24": job51_.JobAkParse,
    "24": spider_job_impl.JOBAKParse,
    "25": maigo_by_company.Maigo_Company,
    "26": wutong_thread.WuTongParse,
    "27": qymgc.Spider,
    "28": recruit_thread.ZhilianRecruitParse,
    "29": sole.Spider,
    "31": zhaopin51.Spider,
    "c1": query_phone.Spider,
    "c2": filter_phone_number.FILTERPHONE,
    "c3": extract_city.Clean,
    "c4": filter_abbreviation.FILTEABBREVIATION,
    "c5": filter_company.FILTERCOMPANY,
    "c6": sacle_clean.ScaleClean,
    "c7": info_clean.InfoClean,
    "c8": match_company.MatchCompany,
    "c9": info_contain.InfoContain,
    "a33": job51_company.JobCK,
    '33': spider_job_impl.JOBCK,
    "35": spider_job_impl.JOBID,
    "37": qichacha.QICHACHA,
    "39": tianyancha.TianYanCha,
    "41": zhiyouji.Spider,
    "43": asyncio_baidu.Baidu,
    "45": wutong_thread.WuTongCompany,
    "49": liepinDownByID.DownById,
    "51": job51downByID.Job51,
    "53": zhiliandownByID.ZhiLianDownByID,
    "55": qichacha_.QiChaCha,

}
