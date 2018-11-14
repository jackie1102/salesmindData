# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='JobId',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('create_time', models.DateTimeField(help_text='创建时间', auto_now_add=True)),
                ('update_time', models.DateTimeField(help_text='更新时间', auto_now=True)),
                ('is_delete', models.BooleanField(default=False, help_text='删除标记')),
                ('vipname', models.CharField(max_length=30, help_text='会员名称')),
                ('username', models.CharField(max_length=30, help_text='用户名')),
                ('password', models.CharField(max_length=40, help_text='密码')),
                ('status', models.IntegerField(default=0, help_text='是否被占用')),
                ('task_id', models.IntegerField(default=0, help_text='占用任务ID')),
            ],
            options={
                'db_table': 'JobUser',
            },
        ),
        migrations.CreateModel(
            name='SpiderData',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('create_time', models.DateTimeField(help_text='创建时间', auto_now_add=True)),
                ('update_time', models.DateTimeField(help_text='更新时间', auto_now=True)),
                ('is_delete', models.BooleanField(default=False, help_text='删除标记')),
                ('data', models.TextField(help_text='待抓取的url或者公司')),
            ],
            options={
                'db_table': 'task_data',
            },
        ),
        migrations.CreateModel(
            name='SpiderTask',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('create_time', models.DateTimeField(help_text='创建时间', auto_now_add=True)),
                ('update_time', models.DateTimeField(help_text='更新时间', auto_now=True)),
                ('is_delete', models.BooleanField(default=False, help_text='删除标记')),
                ('spider_id', models.CharField(max_length=30, help_text='爬虫id')),
                ('table_name', models.CharField(max_length=40, help_text='下载表名')),
                ('status_1', models.IntegerField(default=0, help_text='运行状态1')),
                ('status_2', models.IntegerField(default=0, help_text='运行状态2')),
                ('user_id', models.IntegerField(help_text='用户id')),
                ('param', models.TextField(help_text='配置参数')),
                ('data_totle', models.IntegerField(default=0, help_text='data总数')),
                ('progress', models.IntegerField(default=0, help_text='已经爬取data数量百分比')),
                ('download_status', models.IntegerField(default=0, help_text='下载状态')),
            ],
            options={
                'db_table': 'python_task',
            },
        ),
        migrations.CreateModel(
            name='ZhiLianId',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('create_time', models.DateTimeField(help_text='创建时间', auto_now_add=True)),
                ('update_time', models.DateTimeField(help_text='更新时间', auto_now=True)),
                ('is_delete', models.BooleanField(default=False, help_text='删除标记')),
                ('username', models.CharField(max_length=30, help_text='用户名')),
                ('password', models.CharField(max_length=40, help_text='密码')),
                ('status', models.IntegerField(default=0, help_text='是否被占用')),
                ('task_id', models.IntegerField(default=0, help_text='占用任务ID')),
            ],
            options={
                'db_table': 'ZhiLianUser',
            },
        ),
        migrations.AddField(
            model_name='spiderdata',
            name='data_task',
            field=models.ForeignKey(to='spider.SpiderTask'),
        ),
    ]
