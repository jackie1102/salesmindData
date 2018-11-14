# coding=utf-8
# 定义抽象模型类
from django.db import models


class BaseModel(models.Model):
    '''
    抽象模型类
    '''
    create_time = models.DateTimeField(auto_now_add=True, help_text='创建时间')
    update_time = models.DateTimeField(auto_now=True, help_text='更新时间')
    is_delete = models.BooleanField(default=False, help_text='删除标记')

    class Meta:
        abstract = True # 模型类是抽象的