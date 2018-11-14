import copy
from django.shortcuts import render
from django.http import JsonResponse
from django.http import HttpResponse
from pymongo import MongoClient
from xlwt import *
import xlrd
from spider.models import *
from utils.deacrators import interceptor
from utils.respcode import *
import io
from utils.utils import *
from utils.jobcondition import *


@interceptor
def index(request):
    """
    进入首页
    :param request:
    :return:
    """
    return render(request, 'index.html')


@interceptor
def reptile(request):
    """
    进入爬虫分类
    :param request:
    :return:
    """
    return render(request, 'reptile/reptile.html')


@interceptor
def qymgc(request):
    """
    进入买购网页面
    :param request:
    :return:
    """
    return render(request, "spider/qymgc/qymgc.html")


@interceptor
def maigo(request):
    """
    进入买购网页面
    :param request:
    :return:
    """
    return render(request, "spider/maigo/maigo.html")


@interceptor
def liepin_prev(request):
    '''
    去51Sole网页面
    :param request:
    :return:
    '''
    return render(request, "spider/liepin_prev/liepin_prev.html")


@interceptor
def sole(request):
    '''
    去51Sole网页面
    :param request:
    :return:
    '''
    return render(request, "spider/sole/sole.html")


@interceptor
def boss(request):
    '''
    去BOSS直聘页面
    :param request:
    :return:
    '''
    return render(request, "spider/boss/boss.html")


@interceptor
def kanzhunwang(request):
    '''
    去百度百聘页面
    :param request:
    :return:
    '''
    return render(request, "spider/kanzhunwang/kanzhunwang.html")


@interceptor
def zhiyouji(request):
    '''
    去百度百聘页面
    :param request:
    :return:
    '''
    return render(request, "spider/zhiyouji/zhiyouji.html")


@interceptor
def zhilian51(request):
    '''
    去百度百聘页面
    :param request:
    :return:
    '''
    return render(request, "spider/zhaopin51(baidu)/zhaopin51.html")


@interceptor
def baidubaipin(request):
    '''
    去百度百聘页面
    :param request:
    :return:
    '''
    return render(request, "spider/baidubaipin/baidubaipin.html")


@interceptor
def email(request):
    '''
    去智联页面
    :param request:
    :return:
    '''
    return render(request, "spider/email/email.html")


@interceptor
def zhaopin(request):
    '''
    去智联页面
    :param request:
    :return:
    '''
    return render(request, "spider/zhaopin/zhaopin.html")


@interceptor
def zdao(request):
    '''
    去早稻页面
    :param request:
    :return:
    '''
    return render(request, "spider/zdao/zdao.html")


@interceptor
def liepin(request):
    '''
    去猎聘页面
    :param request:
    :return:
    '''
    return render(request, "spider/liepin/liepin.html")


@interceptor
def job51(request):
    '''
    去前程无忧页面
    :param request:
    :return:
    '''
    return render(request, "spider/job51/job51.html")


@interceptor
def open_job51_industry(request):
    '''
    去前程无忧行业页面
    :param request:
    :return:
    '''
    return render(request, "spider/job51/condition/industry.html")


@interceptor
def open_job51_area(request):
    '''
    去前程无忧地区页面
    :param request:
    :return:
    '''
    return render(request, "spider/job51/condition/area.html")


@interceptor
def open_job51_jobs(request):
    '''
    去前程无忧职能页面
    :param request:
    :return:
    '''
    return render(request, "spider/job51/condition/job.html")


@interceptor
def open_job51_exp_area(request):
    '''
    去前程无忧期望工作地页面
    :param request:
    :return:
    '''
    return render(request, "spider/job51/condition/exp_area.html")


@interceptor
def open_job51_major(request):
    '''
    去前程无忧专业页面
    :param request:
    :return:
    '''
    return render(request, "spider/job51/condition/major.html")


@interceptor
def open_job51_residence(request):
    '''
    去前程无忧户口所在地页面
    :param request:
    :return:
    '''
    return render(request, "spider/job51/condition/residence.html")


@interceptor
def qichacha(request):
    '''
    去企查查页面
    :param request:
    :return:
    '''
    return render(request, "spider/qichacha/qichacha.html")


@interceptor
def qichacha_(request):
    '''
    去企查查页面
    :param request:
    :return:
    '''
    return render(request, "spider/qichacha/qichacha_.html")


@interceptor
def tianyancha(request):
    '''
    去天眼查页面
    :param request:
    :return:
    '''
    return render(request, "spider/tianyancha/tianyancha.html")


@interceptor
def itjuzi(request):
    '''
    去IT桔子页面
    :param request:
    :return:
    '''
    return render(request, "spider/itjuzi/itjuzi.html")


@interceptor
def open_itjuzi_industry(request):
    '''
    去IT桔子行业页面
    :param request:
    :return:
    '''
    return render(request, "spider/itjuzi/condition/industry.html")


@interceptor
def lagou(request):
    '''
    去拉勾页面
    :param request:
    :return:
    '''
    return render(request, "spider/lagou/lagou.html")


@interceptor
def wutong(request):
    """
    去物通网爬虫页面
    :param request:
    :return:
    """
    return render(request, "spider/wutong/wutong.html")


@interceptor
def jincheng(request):
    """
    去锦程网爬虫页面
    :param request:
    :return:
    """
    return render(request, "spider/jincheng/jincheng.html")


@interceptor
def mergespider(request):
    """
    去锦程网爬虫页面
    :param request:
    :return:
    """
    return render(request, "spider/mergespider/mergespider.html")


@interceptor
def zhilian_recruit(request):
    """
    智联前台招聘职位
    :param request:
    :return:
    """
    return render(request, "spider/zhilian_recruit/zhilian_recruit.html")


@interceptor
def wuba_recruit(request):
    """
    58同城招聘职位
    :param request:
    :return:
    """
    return render(request, "spider/wubatongcheng/wubatongcheng.html")


@interceptor
def ganji_recruit(request):
    """
    赶集网招聘职位
    :param request:
    :return:
    """
    return render(request, "spider/ganji/ganji.html")


@interceptor
def recruit_51(request):
    """
    前程无忧前台职位招聘
    :param request:
    :return:
    """
    return render(request, "spider/recruit_51/recruit_51.html")


@interceptor
def chuangyebang(request):
    """
    创业帮投融资信息
    :param request:
    :return:
    """
    return render(request, "spider/chuangyebang/chuangyebang.html")


@interceptor
def atubo(request):
    """
    阿土伯公司采集
    :param request:
    :return:
    """
    return render(request, "spider/atubo/atubo.html")


@interceptor
def baidu(request):
    """
    百度官网加V认证
    :param request:
    :return:
    """
    return render(request, "spider/baidu/baidu.html")


@interceptor
def shunqi(request):
    '''
    去顺企页面
    :param request:
    :return:
    '''
    return render(request, "spider/shunqi/shunqi.html")


@interceptor
def operation(request):
    task_id = request.GET.get('task_id')
    obj = SpiderTask.objects.get_one_task(id=task_id)
    task = {}
    task["task_id"] = task_id
    task['spider_id'] = obj.spider_id
    task["table_name"] = json.loads(obj.param).get('table_name')
    task["start_time"] = str(obj.create_time).split('.')[0]
    if obj.status_1 == 0:
        task["state_1"] = "未启动"
    elif obj.status_1 == 1:
        task["state_1"] = "运行中"
    elif obj.status_1 == 2:
        task["state_1"] = "已完成"
    else:
        task["state_1"] = "已中断"
    if obj.status_2 == 0:
        task["state_2"] = "未启动"
    elif obj.status_2 == 1:
        task["state_2"] = "运行中"
    elif obj.status_2 == 2:
        task["state_2"] = "已完成"
    else:
        task["state_2"] = "已中断"
    return render(request, "home/operation.html", context={'task': task})


@interceptor
def down_file(request):
    '''
    下载Excel
    '''
    task_id = request.GET.get("task_id")
    obj = SpiderTask.objects.get_one_task(id=task_id)
    tablename = json.loads(obj.param).get('table_name')
    # client = MongoClient(host="139.196.29.181", port=27017)
    client = MongoClient(host="127.0.0.1", port=27017)
    db = client['salesmindSpider']
    # db.authenticate("spider1", "123456")
    col = db['Miindai_salesmind_' + tablename.split('-')[0] + '_' + str(task_id)]
    rows = col.find()
    ws = Workbook(encoding='utf-8')
    shee = ws.add_sheet('sheet1')
    try:
        key_list = []
        for key in list(rows[0].keys()):
            if key == "_id" or key == "date":
                continue
            else:
                key_list.append(key)
        sheet_num = 1
        key_list.sort()
        key_list.reverse()
        for element in key_list:
            shee.write(0, key_list.index(element), element)
        row_index = 1
        for row in rows:
            values = []
            for key in key_list:
                try:
                    values.append(row[key])
                except:
                    values.append('-')
            column = 0
            for value in values:
                if len(str(value)) < 32767:
                    try:
                        shee.write(row_index, column, value)
                    except Exception as E:
                        print(E)
                column += 1
            row_index += 1
            if row_index > 60000:
                sheet_num += 1
                shee = ws.add_sheet('sheet{}'.format(sheet_num))
                row_index = 0
    except Exception as E:
        print(E)
        # shee.write(0, 0, '未抓取到数据')
    sio = io.BytesIO()
    ws.save(sio)
    sio.seek(0)
    response = HttpResponse(sio.getvalue(), content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment;filename={}.xlsx'.format(
        tablename.encode('gb2312').decode('iso-8859-1'))
    response.write(sio.getvalue())
    obj.download_status = 1
    obj.save()
    return response


@interceptor
def stop_task1(request):
    '''
    停止爬虫线程
    :param request:
    :return:
    '''
    try:
        task_id = request.POST.get('task_id')
        task = SpiderTask.objects.get_one_task(id=task_id)
        task.status_1 = 3
        task.save()
        resd = {"errId": SUCCESS, "errMsg": RESP_CODE.get(SUCCESS)}
    except Exception as e:
        resd = {"errId": THREAD_SYSTEM_ERROR, "errMsg": str(e)}
    return JsonResponse(resd)


@interceptor
def stop_task2(request):
    '''
    停止爬虫线程
    :param request:
    :return:
    '''
    try:
        task_id = request.POST.get('task_id')
        task = SpiderTask.objects.get_one_task(id=task_id)
        task.status_2 = 3
        task.save()
        resd = {"errId": SUCCESS, "errMsg": RESP_CODE.get(SUCCESS)}
    except Exception as e:
        resd = {"errId": THREAD_SYSTEM_ERROR, "errMsg": str(e)}
    return JsonResponse(resd)

@interceptor
def del_task(request):
    '''
    删除爬虫任务
    :param request:
    :return:
    '''
    try:
        task_id = request.POST.get("task_id")
        SpiderData.objects.filter(data_task_id=task_id).delete()
        task = SpiderTask.objects.get_one_task(id=task_id)
        task.data_totle = 0
        task.status_1 = 0
        task.is_delete = 1
        task.save()
        res = {"errId": SUCCESS, "errMsg": RESP_CODE.get(SUCCESS)}
    except Exception as e:
        res = {"errId": UNKNOWN_SYS_ERROR, "errMsg": str(e)}
    return JsonResponse(res)


@interceptor
def create_task(request):
    '''
    运行智联爬虫(关键词搜索)
    :param request:
    :return:
    '''
    try:
        if request.is_ajax() and request.method == 'POST':
            param = {}
            for key in request.POST:
                param[key] = request.POST.get(key)
            table_name = request.POST.get('table_name')
            user_id = request.POST.get('user_id')
            spider_id = request.POST.get('spider_id')
            obj = SpiderTask.objects.add_one_task(table_name=table_name, user_id=user_id, spider_id=spider_id,
                                                  param=json.dumps(param))
            if obj:
                res = {"errId": SUCCESS, "errMsg": RESP_CODE.get(SUCCESS)}
            else:
                res = {"errId": UNKNOWN_SYS_ERROR, "errMsg": '下载文件名已存在'}
        else:
            res = {"errId": UNKNOWN_SYS_ERROR, "errMsg": '无效的请求'}
    except Exception as e:
        res = {"errId": UNKNOWN_SYS_ERROR, "errMsg": str(e)}
    return JsonResponse(res)


@interceptor
def create_task_zhilian_condition(request):
    try:
        if request.is_ajax() and request.method == 'POST':
            # 参数形式
            data = {"start": 0, "rows": 30, "S_DISCLOSURE_LEVEL": 2, "S_EXCLUSIVE_COMPANY": "上海门迪智能科技有限公司",
                    "S_KEYWORD": "", "S_DATE_MODIFIED": "", "S_CURRENT_CITY": "",
                    "S_JOB_TYPE_ALL": "", "S_INDUSTRY_ALL": "", "S_CURRENT_CAREER_STATUS": "",
                    "S_ENGLISH_RESUME": "1", "isrepeat": 1, "sort": "date"}
            # 爬虫ID
            spider_id = request.POST.get('spider_id')
            # 用户id
            user_id = request.POST.get('user_id')
            # 关键词
            keywords = request.POST.get('keywords', '').strip().replace(' ', ';')
            # 职位
            position = request.POST.get('position', '').strip().split(' ')
            # 行业
            industry = request.POST.get('industry', '').strip().split(' ')
            # 地区
            addr = request.POST.get('addr', '').strip().split(' ')
            # 工作状态
            status = request.POST.get('status', '').strip().split(' ')
            # 更新时间
            update = ZHILIAN_UPDATE.get(request.POST.get('update', '-'), '').strip().split(' ')
            # 下载文件名
            table_name = request.POST.get('table_name')
            # 参数列表
            item_list = []
            for ps in position:
                for ind in industry:
                    for ad in addr:
                        for st in status:
                            for ud in update:
                                item = [keywords, ps, ind, ad, st, ud]
                                item_list.append(item)
            # 生成任务参数
            for item in item_list:
                param = {}
                param["spider_id"] = spider_id
                param["user_id"] = user_id
                param["table_name"] = table_name + '_' + str(item_list.index(item))
                data["S_KEYWORD"] = item[0]
                data["S_JOB_TYPE_ALL"] = item[1]
                data["S_INDUSTRY_ALL"] = item[2]
                data["S_CURRENT_CITY"] = item[3]
                data["S_CURRENT_CAREER_STATUS"] = item[4]
                data["S_DATE_MODIFIED"] = item[5]
                data1 = copy.copy(data)
                for key in data1.keys():
                    if data1[key] == '':
                        data.pop(key)
                param["param"] = str(data).replace('\'', '\"')
                # 生成任务
                obj = SpiderTask.objects.add_one_task(table_name=table_name + '_' + str(item_list.index(item)), user_id=user_id,
                                                      spider_id=spider_id, param=json.dumps(param))
                if obj:
                    pass
                else:
                    res = {"errId": UNKNOWN_SYS_ERROR, "errMsg": '下载文件名已存在'}
                    break
            else:
                res = {"errId": SUCCESS, "errMsg": RESP_CODE.get(SUCCESS)}
        else:
            res = {"errId": UNKNOWN_SYS_ERROR, "errMsg": '无效的请求'}
    except Exception as e:
        res = {"errId": UNKNOWN_SYS_ERROR, "errMsg": str(e)}
    return JsonResponse(res)


@interceptor
def create_task_zhilian_company(request):
    try:
        if request.is_ajax() and request.method == 'POST':
            # 读取上传文件
            wb = xlrd.open_workbook(filename=None, file_contents=request.FILES["file"].read())
            # 参数形式
            data = {"start": 0, "rows": 30, "S_DISCLOSURE_LEVEL": 2, "S_EXCLUSIVE_COMPANY": "上海门迪智能科技有限公司",
                    "S_KEYWORD": "", "S_DATE_MODIFIED": "", "S_CURRENT_CITY": "",
                    "S_JOB_TYPE_ALL": "", "S_INDUSTRY_ALL": "", "S_CURRENT_CAREER_STATUS": "",
                    "S_ENGLISH_RESUME": "1", "isrepeat": 1, "sort": "date"}
            # 爬虫ID
            spider_id = request.POST.get('spider_id')
            # 用户id
            user_id = request.POST.get('user_id')
            # 关键词
            keywords = request.POST.get('keywords', '').strip().replace(' ', ';')
            # 职位
            position = request.POST.get('position', '').strip().split(' ')
            # 行业
            industry = request.POST.get('industry', '').strip().split(' ')
            # 地区
            addr = request.POST.get('addr', '').strip().split(' ')
            # 工作状态
            status = request.POST.get('status', '').strip().split(' ')
            # 更新时间
            update = ZHILIAN_UPDATE.get(request.POST.get('update'), '').strip().split(' ')
            # 最近公司
            last = request.POST.get('last')
            # 下载文件名
            table_name = request.POST.get('table_name')
            # 参数列表
            item_list = []
            for ps in position:
                for ind in industry:
                    for ad in addr:
                        for st in status:
                            for ud in update:
                                item = [keywords, ps, ind, ad, st, ud]
                                item_list.append(item)
            # 生成任务参数
            for item in item_list:
                param = {}
                param["spider_id"] = spider_id
                param["user_id"] = user_id
                param["table_name"] = table_name + '_' + str(item_list.index(item))
                param['last'] = last
                data["S_KEYWORD"] = item[0]
                data["S_JOB_TYPE_ALL"] = item[1]
                data["S_INDUSTRY_ALL"] = item[2]
                data["S_CURRENT_CITY"] = item[3]
                data["S_CURRENT_CAREER_STATUS"] = item[4]
                data["S_DATE_MODIFIED"] = item[5]
                data1 = copy.copy(data)
                for key in data1.keys():
                    if data1[key] == '':
                        data.pop(key)
                param["param"] = str(data).replace('\'', '\"')
                # 生成任务
                obj = SpiderTask.objects.add_one_task(table_name=table_name + '_' + str(item_list.index(item)), user_id=user_id,
                                                      spider_id=spider_id, param=json.dumps(param))
                if obj:
                    table = wb.sheets()[0]
                    rows = table.nrows
                    data_list = []
                    for i in range(0, rows):
                        col = table.row_values(i)
                        data_list.append(col[0])
                    SpiderData.objects.add_data_list(data_list=data_list, task_id=obj.id)
                    task = SpiderTask.objects.get_one_task(id=obj.id)
                    task.data_totle = len(data_list) + task.data_totle
                    task.save()
                    SpiderTask.objects.finish_task1(task_id=obj.id)
                else:
                    res = {"errId": UNKNOWN_SYS_ERROR, "errMsg": '下载文件名已存在'}
                    break
            else:
                res = {"errId": SUCCESS, "errMsg": RESP_CODE.get(SUCCESS)}
        else:
            res = {"errId": UNKNOWN_SYS_ERROR, "errMsg": '无效的请求'}
    except Exception as e:
        res = {"errId": UNKNOWN_SYS_ERROR, "errMsg": str(e)}
    return JsonResponse(res)


@interceptor
def create_task_job_condition(request):
    try:
        if request.is_ajax() and request.method == 'POST':
            # 参数形式 {关键词}#{居住地}#0#{职位}#{行业}##################{更新日期}#{在职状态}#1#0###0#{职位含期望}#{行业含期望}
            data_str = '{}#{}#0#{}#{}##################{}#{}#1#0###0#{}#{}'
            # 爬虫ID
            spider_id = request.POST.get('spider_id')
            # 用户id
            user_id = request.POST.get('user_id')
            # 关键词
            keywords = request.POST.get('keywords', '').strip()
            # 职位
            position = request.POST.get('position', '').strip().split(' ')
            # 行业
            industry = request.POST.get('industry', '').strip().split(' ')
            # 地区
            addr = request.POST.get('addr', '').strip().split(' ')
            # 工作状态
            status = request.POST.get('status', '').strip().split(' ')
            # 更新时间
            update = request.POST.get('update', '').strip().split(' ')
            # 下载文件名
            table_name = request.POST.get('table_name')
            # 最近行业
            onlyindustry = request.POST.get('onlyIndustry')
            if onlyindustry == 'on':
                onlyindustry = '1'
            else:
                onlyindustry = '0'
            # 最近职能
            only_fun = request.POST.get('only_fun')
            if only_fun == 'on':
                only_fun = '1'
            else:
                only_fun = '0'
            # 参数列表
            item_list = []
            for ps in position:
                for ind in industry:
                    for ad in addr:
                        for st in status:
                            for ud in update:
                                item = [keywords, JOB_POSITION.get(ps), JOB_INDUSTRY.get(ind), JOB_AREA.get(ad), JOB_STATUS.get(st), JOB_UPDATE.get(ud)]
                                item_list.append(item)
            # 生成任务参数
            for item in item_list:
                param = {}
                param["spider_id"] = spider_id
                param["user_id"] = user_id
                param["table_name"] = table_name + '_' + str(item_list.index(item))
                param["param"] = data_str.format(item[0], item[3], item[1], item[2], item[5], item[4], only_fun, onlyindustry)
                # 生成任务
                obj = SpiderTask.objects.add_one_task(table_name=table_name + '_' + str(item_list.index(item)), user_id=user_id,
                                                      spider_id=spider_id, param=json.dumps(param))
                if obj:
                    pass
                else:
                    res = {"errId": UNKNOWN_SYS_ERROR, "errMsg": '下载文件名已存在'}
                    break
            else:
                res = {"errId": SUCCESS, "errMsg": RESP_CODE.get(SUCCESS)}
        else:
            res = {"errId": UNKNOWN_SYS_ERROR, "errMsg": '无效的请求'}
    except Exception as e:
        res = {"errId": UNKNOWN_SYS_ERROR, "errMsg": str(e)}
    return JsonResponse(res)

@interceptor
def create_task_job_company(request):
    try:
        if request.is_ajax() and request.method == 'POST':
            # 参数形式 {关键词}#{居住地}#0#{职位}#{行业}##################{更新日期}#{在职状态}#1#0###0#{职位含期望}#{行业含期望}
            data_str = '{}#{}#0#{}#{}#######//###########{}#{}#1#0###0#{}#{}'
            # 读取上传文件
            wb = xlrd.open_workbook(filename=None, file_contents=request.FILES["file"].read())
            # 爬虫ID
            spider_id = request.POST.get('spider_id')
            # 用户id
            user_id = request.POST.get('user_id')
            # 关键词
            keywords = request.POST.get('keywords', '').strip()
            # 职位
            position = request.POST.get('position', '').strip().split(' ')
            # 行业
            industry = request.POST.get('industry', '').strip().split(' ')
            # 地区
            addr = request.POST.get('addr', '').strip().split(' ')
            # 工作状态
            status = request.POST.get('status', '').strip().split(' ')
            # 更新时间
            update = request.POST.get('update', '').strip().split(' ')
            # 最近行业
            onlyindustry = request.POST.get('onlyIndustry')
            if onlyindustry == 'on':
                onlyindustry = '1'
            else:
                onlyindustry = '0'
            # 最近职能
            only_fun = request.POST.get('only_fun')
            if only_fun == 'on':
                only_fun = '1'
            else:
                only_fun = '0'
            # 最近公司
            last = request.POST.get('last')
            # 下载文件名
            table_name = request.POST.get('table_name')
            # 参数列表
            item_list = []
            for ps in position:
                for ind in industry:
                    for ad in addr:
                        for st in status:
                            for ud in update:
                                item = [keywords, JOB_POSITION.get(ps), JOB_INDUSTRY.get(ind), JOB_AREA.get(ad), JOB_STATUS.get(st), JOB_UPDATE.get(ud)]
                                item_list.append(item)
            # 生成任务参数
            for item in item_list:
                param = {}
                param["spider_id"] = spider_id
                param["user_id"] = user_id
                param["table_name"] = table_name + '_' + str(item_list.index(item))
                param['last'] = last
                param["param"] = data_str.format(item[0], item[3], item[1], item[2], item[5], item[4], only_fun, onlyindustry).replace('//', '{}')
                # 生成任务
                obj = SpiderTask.objects.add_one_task(table_name=table_name + '_' + str(item_list.index(item)), user_id=user_id,
                                                      spider_id=spider_id, param=json.dumps(param))
                if obj:
                    table = wb.sheets()[0]
                    rows = table.nrows
                    data_list = []
                    for i in range(0, rows):
                        col = table.row_values(i)
                        data_list.append(col[0])
                    SpiderData.objects.add_data_list(data_list=data_list, task_id=obj.id)
                    task = SpiderTask.objects.get_one_task(id=obj.id)
                    task.data_totle = len(data_list) + task.data_totle
                    task.save()
                    SpiderTask.objects.finish_task1(task_id=obj.id)
                else:
                    res = {"errId": UNKNOWN_SYS_ERROR, "errMsg": '下载文件名已存在'}
                    break
            else:
                res = {"errId": SUCCESS, "errMsg": RESP_CODE.get(SUCCESS)}
        else:
            res = {"errId": UNKNOWN_SYS_ERROR, "errMsg": '无效的请求'}
    except Exception as e:
        res = {"errId": UNKNOWN_SYS_ERROR, "errMsg": str(e)}
    return JsonResponse(res)


@interceptor
def start_task1(request):
    spider_id = request.POST.get('spider_id')
    task_id = request.POST.get('task_id')
    try:
        if 'c' not in str(spider_id):
            if 'a' in spider_id:
                spider_id = spider_id.replace('a', '')
            if int(spider_id) % 2 == 0:
                SpiderTask.objects.start_task1(task_id=task_id)
            else:
                wb = xlrd.open_workbook(filename=None, file_contents=request.FILES["file"].read())
                table = wb.sheets()[0]
                rows = table.nrows
                data_list = []
                for i in range(0, rows):
                    col = table.row_values(i)
                    data_list.append(col[0])
                SpiderData.objects.add_data_list(data_list=data_list, task_id=task_id)
                task = SpiderTask.objects.get_one_task(id=task_id)
                task.data_totle = len(data_list) + task.data_totle
                task.save()
                SpiderTask.objects.finish_task1(task_id=task_id)
            res = {"errId": SUCCESS, "errMsg": RESP_CODE.get(SUCCESS)}
        else:
            wb = xlrd.open_workbook(filename=None, file_contents=request.FILES["file"].read())
            table = wb.sheets()[0]
            rows = table.nrows
            data_list = []
            key_list = table.row_values(0)
            for i in range(1, rows):
                item = {}
                value_list = table.row_values(i)
                for key, value in zip(key_list, value_list):
                    item[key] = value
                data_list.append(json.dumps(item))
            SpiderData.objects.add_data_list(data_list=data_list, task_id=task_id)
            task = SpiderTask.objects.get_one_task(id=task_id)
            task.data_totle = len(data_list) + task.data_totle
            task.save()
            SpiderTask.objects.finish_task1(task_id=task_id)
            res = {"errId": SUCCESS, "errMsg": RESP_CODE.get(SUCCESS)}
    except Exception as E:
        res = {"errId": UNKNOWN_SYS_ERROR, "errMsg": str(E)}
    return JsonResponse(res)


@interceptor
def start_task2(request):
    task_id = request.POST.get('task_id')
    try:
        SpiderTask.objects.start_task2(task_id=task_id)
        res = {"errId": SUCCESS, "errMsg": RESP_CODE.get(SUCCESS)}
    except Exception as E:
        res = {"errId": UNKNOWN_SYS_ERROR, "errMsg": str(E)}
    return JsonResponse(res)


@interceptor
def showparam(request):
    """
    展示配置参数
    :param request:
    :return:
    """
    task_id = request.POST.get('task_id')
    task = SpiderTask.objects.get_one_task(id=task_id)
    param = str(json.loads(task.param))
    print(param)
    return JsonResponse({"errId": SUCCESS, "param": param})


@interceptor
def open_alter_param(request):
    return render(request, 'home/alter_param.html')


@interceptor
def alter_param(request):
    """
    修改配置参数
    :param request:
    :return:
    """
    try:
        task_id = request.POST.get('task_id')
        param = json.loads(request.POST.get('param').replace('\"', '***').replace('\'', '\"'))
        task = SpiderTask.objects.get_one_task(id=task_id)
        data = json.dumps(param)
        data = data.replace('***', '\\\"')
        task.param = data
        task.save()
        res = {'errId': SUCCESS}
    except Exception as E:
        print(E)
        res = {'errId': UNKNOWN_SYS_ERROR, 'errMsg': str(E)}
    return JsonResponse(res)


@interceptor
def show_data(request):
    """
    展示10分钟以内采集的数据
    :param request:
    :return:
    """
    task_id = request.POST.get('task_id')
    obj = SpiderTask.objects.get_one_task(id=task_id)
    tablename = json.loads(obj.param).get('table_name')
    # client = MongoClient(host="139.196.29.181", port=27017)
    client = MongoClient(host="127.0.0.1", port=27017)
    db = client['salesmindSpider']
    # db.authenticate("spider1", "123456")
    col = db['Miindai_salesmind_' + tablename.split('-')[0] + '_' + str(task_id)]
    timestamp = int(time.time()) - 600
    rows = col.find({'date': {'$gte': timestamp}})
    items = ''
    for item in rows:
        item.pop('_id')
        items += '<p>{}</p>'.format(str(item))
    return JsonResponse({'errId': SUCCESS, 'item': items})


@interceptor
def clear_data(request):
    """
    删除上传数据或采集的url
    :param request:
    :return:
    """
    try:
        task_id = request.POST.get('task_id')
        SpiderData.objects.filter(data_task_id=task_id).delete()
        task = SpiderTask.objects.get_one_task(id=task_id)
        task.data_totle = 0
        task.status_1 = 0
        task.status_2 = 0
        task.download_status = 0
        task.save()
        res = {"errId": SUCCESS, "errMsg": RESP_CODE.get(SUCCESS)}
    except Exception as E:
        res = {'errID': UNKNOWN_SYS_ERROR, 'errMsg': str(E)}
    return JsonResponse(res)


def auto_zhilian(request):
    """
    自动后台
    :param request:
    :return:
    """
    return render(request, 'auto_houtai/auto_zhilian.html')


def check_zhilian_position(request):
    position = request.GET.get('position')
    position_list = position.split(' ')
    sign = True
    ms = ''
    for ps in position_list:
        if ps not in list(ZHILIAN_POSITION.keys()):
            sign = False
            ms += ps + '；'
    if sign:
        res = {"errId": SUCCESS, "errMsg": RESP_CODE.get(SUCCESS)}
    else:
        res = {"errId": ERROR, "errMsg": ms[:-1] + RESP_CODE.get(ERROR)}
    return JsonResponse(res)


def check_zhilian_addr(request):
    addr = request.GET.get('addr')
    addr_list = addr.split(' ')
    sign = True
    ms = ''
    for ad in addr_list:
        if ad not in list(ZHILIAN_ADDR.keys()):
            sign = False
            ms += ad + '；'
    if sign:
        res = {"errId": SUCCESS, "errMsg": RESP_CODE.get(SUCCESS)}
    else:
        res = {"errId": ERROR, "errMsg": ms[:-1] + RESP_CODE.get(ERROR)}
    return JsonResponse(res)


def check_zhilian_industry(request):
    industry = request.GET.get('industry')
    industry_list = industry.split(' ')
    sign = True
    ms = ''
    for ind in industry_list:
        if ind not in list(ZHILIAN_INDUSTRY.keys()):
            sign = False
            ms += ind + '；'
    if sign:
        res = {"errId": SUCCESS, "errMsg": RESP_CODE.get(SUCCESS)}
    else:
        res = {"errId": ERROR, "errMsg": ms[:-1] + RESP_CODE.get(ERROR)}
    return JsonResponse(res)


def check_zhilian_update(request):
    update = request.GET.get('update')
    update_list = update.split(' ')
    sign = True
    ms = ''
    for ud in update_list:
        if ud not in list(ZHILIAN_UPDATE.keys()):
            sign = False
            ms += ud + '；'
    if sign:
        res = {"errId": SUCCESS, "errMsg": RESP_CODE.get(SUCCESS)}
    else:
        res = {"errId": ERROR, "errMsg": ms[:-1] + RESP_CODE.get(ERROR)}
    return JsonResponse(res)

def check_zhilian_status(request):
    status = request.GET.get('status')
    status_list = status.split(' ')
    sign = True
    ms = ''
    for st in status_list:
        if st not in list(ZHILIAN_STATUS.keys()):
            sign = False
            ms += st + '；'
    if sign:
        res = {"errId": SUCCESS, "errMsg": RESP_CODE.get(SUCCESS)}
    else:
        res = {"errId": ERROR, "errMsg": ms[:-1] + RESP_CODE.get(ERROR)}
    return JsonResponse(res)


def auto_job(request):
    """
    自动后台
    :param request:
    :return:
    """
    return render(request, 'auto_houtai/auto_51.html')


def check_job_position(request):
    position = request.GET.get('position')
    position_list = position.split(' ')
    sign = True
    ms = ''
    for ps in position_list:
        if ps not in list(JOB_POSITION.keys()):
            sign = False
            ms += ps + '；'
    if sign:
        res = {"errId": SUCCESS, "errMsg": RESP_CODE.get(SUCCESS)}
    else:
        res = {"errId": ERROR, "errMsg": ms[:-1] + RESP_CODE.get(ERROR)}
    return JsonResponse(res)


def check_job_addr(request):
    addr = request.GET.get('addr')
    addr_list = addr.split(' ')
    sign = True
    ms = ''
    for ad in addr_list:
        if ad not in list(JOB_AREA.keys()):
            sign = False
            ms += ad + '；'
    if sign:
        res = {"errId": SUCCESS, "errMsg": RESP_CODE.get(SUCCESS)}
    else:
        res = {"errId": ERROR, "errMsg": ms[:-1] + RESP_CODE.get(ERROR)}
    return JsonResponse(res)


def check_job_industry(request):
    industry = request.GET.get('industry')
    industry_list = industry.split(' ')
    sign = True
    ms = ''
    for ind in industry_list:
        if ind not in list(JOB_INDUSTRY.keys()):
            sign = False
            ms += ind + '；'
    if sign:
        res = {"errId": SUCCESS, "errMsg": RESP_CODE.get(SUCCESS)}
    else:
        res = {"errId": ERROR, "errMsg": ms[:-1] + RESP_CODE.get(ERROR)}
    return JsonResponse(res)


def check_job_update(request):
    update = request.GET.get('update')
    update_list = update.split(' ')
    sign = True
    ms = ''
    for ud in update_list:
        if ud not in list(JOB_UPDATE.keys()):
            sign = False
            ms += ud + '；'
    if sign:
        res = {"errId": SUCCESS, "errMsg": RESP_CODE.get(SUCCESS)}
    else:
        res = {"errId": ERROR, "errMsg": ms[:-1] + RESP_CODE.get(ERROR)}
    return JsonResponse(res)


def check_job_status(request):
    status = request.GET.get('status')
    status_list = status.split(' ')
    sign = True
    ms = ''
    for st in status_list:
        if st not in list(JOB_STATUS.keys()):
            sign = False
            ms += st + '；'
    if sign:
        res = {"errId": SUCCESS, "errMsg": RESP_CODE.get(SUCCESS)}
    else:
        res = {"errId": ERROR, "errMsg": ms[:-1] + RESP_CODE.get(ERROR)}
    return JsonResponse(res)