# coding=utf-8
from django.db import models
import copy
# 定义一个模型管理器类的抽象基类


class BaseModelManager(models.Manager):
    '''
    模型管理器类抽象基类
    '''
    def get_all_valid_fields(self):
        '''
        获取模型管理器对象所在模型类的属性列表
        '''
        # 获取模型管理器对象所在的模型类
        cls = self.model
        # 获取cls模型类的属性列表
        attr_list = cls._meta.get_all_field_names()
        return attr_list

    def get_all_valid_fields2(self):
        '''
        获取模型管理器对象所在模型类的属性列表
        '''
        # 获取模型管理器对象所在的模型类
        cls = self.model
        # 获取cls模型类的属性列表
        attr_list = cls._meta.get_fields()
        attr_str_list = []
        for attr in attr_list:
            if isinstance(attr, models.ForeignKey):
                #attr.name = '%s_id'%attr.name
                attr_str = '%s_id'%attr.name
                attr_str_list.append(attr_str)
            else:
                attr_str_list.append(attr.name)
        return attr_str_list

    def create_one_object(self, **kwargs): # passport_id
        '''
        往数据库中插入一条模型管理器对象所在的模型类数据
        '''
        # 获取模型管理器对象所在模型类的属性列表
        vaild_fields = self.get_all_valid_fields2()
        # 拷贝kwargs
        kws = copy.copy(kwargs)

        # 去除模型类无效的属性
        #for k in kws.keys():
        for k in kws:
            if k not in vaild_fields:
                kwargs.pop(k)

        # 获取模型管理器对象所在的模型类
        cls = self.model # Passport
        obj = cls(**kwargs) # Passport(username='smart', password='123',email='smart@itcast.cn')
        # 保存进数据库
        obj.save()

        return obj

    def get_one_object(self, **filters):
        '''
        从数据库表中查出一条模型管理器对象所在模型类的数据
        '''
        try:
            obj = self.get(**filters)
        except self.model.DoesNotExist:
            obj = None
        return obj

    def get_object_list(self, filters={}, exclude_filters={}, order_by=('-pk',), page_index=None, page_size=None):
        '''
        根据过滤条件获取模型管理器对象所在模型类的查询集合
        '''
        # 根据条件获取查询集
        obj_queryset = self.filter(**filters).exclude(**exclude_filters).order_by(*order_by)
        # 对查询结果集进行限制
        #if page_index is not None and page_size is not None:
        if all(map(lambda x:x is not None, (page_index, page_size))):
            start = (page_index-1)*page_size
            end = start + page_size
            obj_queryset = obj_queryset[start:end]

        return obj_queryset



















