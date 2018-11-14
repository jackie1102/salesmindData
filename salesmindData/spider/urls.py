"""salesmindData URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import url
from spider import views

urlpatterns = [
    # 爬虫首页
    url(r'^index/$', views.index),
    # 爬虫分类页
    url(r'^reptile/$', views.reptile),
    # 智联
    url(r'^zhaopin/$', views.zhaopin),

    # 早稻
    url(r'^zdao/$', views.zdao),

    # 猎聘
    url(r'^liepin/$', views.liepin),

    # 猎聘前台
    url(r'^liepin_prev/$', views.liepin_prev),

    # 前程无忧
    url(r'^job51/$', views.job51),
    url(r'^open_job51_industry/$', views.open_job51_industry),
    url(r'^open_job51_area/$', views.open_job51_area),
    url(r'^open_job51_jobs/$', views.open_job51_jobs),
    url(r'^open_job51_exp_area/$', views.open_job51_exp_area),
    url(r'^open_job51_major/$', views.open_job51_major),
    url(r'^open_job51_residence/$', views.open_job51_residence),

    # 企查查
    url(r'^qichacha/$', views.qichacha),

    # 企查查(新)
    url(r'^qichacha_/$', views.qichacha_),

    # 天眼查
    url(r'^tianyancha/$', views.tianyancha),

    # IT桔子
    url(r'^itjuzi/$', views.itjuzi),
    url(r'^open_itjuzi_industry/$', views.open_itjuzi_industry),

    # 拉勾
    url(r'^lagou/$', views.lagou),

    # 顺企
    url(r'^shunqi/$', views.shunqi),

    # 物通网
    url(r'^wutong/$', views.wutong),

    # 锦程物流网
    url(r'^jincheng/$', views.jincheng),

    # 智联招聘前台
    url(r'^zhilian_recruit/$', views.zhilian_recruit),

    # 58同城招聘
    url(r'^wuba_recruit/$', views.wuba_recruit),

    # 赶集网招聘
    url(r'^ganji_recruit/$', views.ganji_recruit),

    # 前程无忧招聘职位
    url(r'^recruit_51job/$', views.recruit_51),

    # 创业帮投融资信息
    url(r'^chuangyebang/$', views.chuangyebang),

    # 阿土伯
    url(r'^atubo/$', views.atubo),

    # 百度官网加V认证
    url(r'^baidu/$', views.baidu),

    # 合并采集
    url(r'^mergespider/$', views.mergespider),

    # 邮箱采集
    url(r'^email/$', views.email),

    # 百度百聘
    url(r'^baidubaipin/$', views.baidubaipin),

    # 智联51百度版
    url(r'^zhilian51/$', views.zhilian51),

    # 职友集
    url(r'^zhiyouji/$', views.zhiyouji),

    # 看准网
    url(r'^kanzhunwang/$', views.kanzhunwang),

    # BOSS直聘
    url(r'^boss/$', views.boss),

    # 买购网
    url(r'^maigoo/$', views.maigo),

    # 51sole网
    url(r'^sole/$', views.sole),

    # 企业梦工厂
    url(r'^qymgc/$', views.qymgc),

    # 自动智联后台
    url(r'^auto_zhilian/$', views.auto_zhilian),

    # 检测智联职位
    url(r'check_zhilian_position/$', views.check_zhilian_position),

    # 检测智联地址
    url(r'check_zhilian_addr/$', views.check_zhilian_addr),

    # 检测智联行业
    url(r'check_zhilian_industry/$', views.check_zhilian_industry),

    # 检测智联更新时间
    url(r'check_zhilian_update/$', views.check_zhilian_update),

    # 检测智联状态
    url(r'check_zhilian_status/$', views.check_zhilian_status),

    # 自动51后台
    url(r'^auto_job/$', views.auto_job),

    # 检测51职位
    url(r'check_job_position/$', views.check_job_position),

    # 检测51地址
    url(r'check_job_addr/$', views.check_job_addr),

    # 检测51行业
    url(r'check_job_industry/$', views.check_job_industry),

    # 检测51更新时间
    url(r'check_job_update/$', views.check_job_update),

    # 检测51状态
    url(r'check_job_status/$', views.check_job_status),

    # 创建任务
    url(r'^create_task/$', views.create_task),

    # 创建智联条件任务
    url(r'^create_task_zhilian_condition/$', views.create_task_zhilian_condition),

    # 创建智联公司任务
    url(r'^create_task_zhilian_company/$', views.create_task_zhilian_company),

    # 创建51job条件任务
    url(r'^create_task_job_condition/$', views.create_task_job_condition),

    # 创建51job公司任务
    url(r'^create_task_job_company/$', views.create_task_job_company),

    # 启动任务
    url(r'^start_task1/$', views.start_task1),
    url(r'^start_task2/$', views.start_task2),

    # 文件上传下载
    # url(r'^upload_file/$', views.upload_file),
    url(r'^down_file/$', views.down_file),

    # 停止任务
    url(r'^stop_task1/$', views.stop_task1),
    url(r'^stop_task2/$', views.stop_task2),

    # 删除任务
    url(r'^del_task/$', views.del_task),

    # 更多操作
    url(r'^operation/$', views.operation),

    # 显示参数
    url(r'^show_param/$', views.showparam),

    # 修改参数
    url(r'^open_alter_param/$', views.open_alter_param),
    url(r'^alter_param/$', views.alter_param),

    # 查看数据
    url(r'^show_data/$', views.show_data),

    # 清除上传数据或采集的url
    url(r'^clear_data/$', views.clear_data),

]
