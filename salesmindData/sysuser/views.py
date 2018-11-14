from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.core.paginator import Paginator
from django.http import JsonResponse
from utils.deacrators import interceptor
from spider.models import SpiderTask
from sysuser.models import Passport
from utils.respcode import *
from utils.utils import USER_ID


def loginPage(request):
    '''
    默认页
    :param request:
    :return:
    '''
    return render(request, 'login.html')


def login(request):
    '''
    用户登录校验
    :param request:
    :return:
    '''
    username = request.POST.get('username')
    password = request.POST.get('password')
    obj = Passport.objects.get_one_passport(username=username, password=password)
    if obj:
        request.session['islogin'] = True
        request.session['userid'] = obj.id
        request.session['nikename'] = obj.nikename
        request.session['username'] = username
        request.session.set_expiry(60 * 60 * 5)
        return JsonResponse({'errId': SUCCESS})
    else:
        return JsonResponse({'errId': USERORPASS_ERROR,'errMsg':RESP_CODE[USERORPASS_ERROR]})

@interceptor
def mytask(request):
    """
    进入任务管理页面
    :param request:
    :return:
    """
    return render(request, 'home/tasks.html')


@interceptor
def tasks(request):
    '''
    主页
    :param request:
    :return:
    '''
    pindex = request.POST.get('page', default=1)
    user = request.POST.get('user')
    userid = USER_ID.get(user) if user else '0'
    create_time = request.POST.get('create_time', default='7')
    if userid:
        task_list = SpiderTask.objects.get_task_list_by_user_id(user_id=userid, create_time=create_time)
        p = Paginator(task_list, 15)
        pindex = int(pindex)
        num_pages = p.num_pages
        if not pindex or pindex > num_pages:
            pindex = 1
        tasks = p.page(pindex)
        current_num = tasks.number
        tasks_ = []
        for task in tasks:
            tasks_.append(task)
        context = {'totle_page': num_pages,'current_page': current_num, 'tasks': tasks_}
        return JsonResponse(context)
    else:
        context = {'totle_page': 1, 'current_page': 1, 'tasks': []}
        return JsonResponse(context)

def logout(request):
    '''
    登出
    :param request:
    :return:
    '''
    request.session.flush()
    return HttpResponseRedirect("/")


def dataC(request):
    return render(request, 'dataC/dataC.html')


def updatelog(request):
    return render(request, 'updatelog.html')