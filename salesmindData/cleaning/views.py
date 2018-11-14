from django.shortcuts import render
from utils.deacrators import interceptor

# Create your views here.



@interceptor
def extract_city(request):
    """
    进入提取城市页面
    :param request:
    :return:
    """
    return render(request, 'cleaning/extract_city/extract_city.html')


@interceptor
def filter_company(request):
    """
    进入筛选公司页面
    :param request:
    :return:
    """
    return render(request, 'cleaning/filter_company/filter_company.html')


@interceptor
def filter_phone_number(request):
    """
    进入筛选公司页面
    :param request:
    :return:
    """
    return render(request, 'cleaning/filter_phone_number/filter_phone_number.html')


def filter_abbreviation(request):
    """
    进入提取公司简称页面
    :param request:
    :return:
    """
    return render(request, 'cleaning/filter_abbreviation/filter_abbreviation.html')


def query_phone(request):
    """
    进入提取公司简称页面
    :param request:
    :return:
    """
    return render(request, 'cleaning/query_phone/query_phone.html')


def scale_clean(request):
    """
    人员规模清洗
    :param request:
    :return:
    """
    return render(request,'cleaning/scale_clean/scale_clean.html')

def info_clean(request):
    """
    公司简介提取部分信息
    :param request:
    :return:
    """
    return render(request,'cleaning/info_clean/info_clean.html')


def match_company(request):
    """
    匹配公司
    :param request:
    :return:
    """
    return render(request, 'cleaning/match_company/match_company.html')


def info_contain(request):
    """
    提取简介中包含的关键词
    :param request:
    :return:
    """
    return render(request, 'cleaning/info_clean/info_contain.html')