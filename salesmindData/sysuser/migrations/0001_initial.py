# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Passport',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('create_time', models.DateTimeField(help_text='创建时间', auto_now_add=True)),
                ('update_time', models.DateTimeField(help_text='更新时间', auto_now=True)),
                ('is_delete', models.BooleanField(default=False, help_text='删除标记')),
                ('username', models.CharField(max_length=20, help_text='用户名')),
                ('password', models.CharField(max_length=40, help_text='密码')),
                ('nikename', models.CharField(max_length=20, help_text='昵称')),
            ],
            options={
                'db_table': 'python_sys_user',
            },
        ),
    ]
