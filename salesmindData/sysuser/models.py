from django.db import models
from db.base_model import BaseModel
from db.base_manager import BaseModelManager
from utils.getHash import get_hash


class PassportManager(BaseModelManager):
    '''
    账户模型管理器类
    '''
    def add_one_passport(self, username, password, nikename):
        '''
        添加一个账户信息
        '''
        obj = self.create_one_object(username=username, password=get_hash(password), nikename=nikename)
        return obj

    def get_one_passport(self, username, password=None):
        '''
        根据用户名和密码查找账户信息
        '''
        ''' 此代码存在bug：只输入正确的用户名就可以实现登录
        if password:
            obj = self.get_one_object(username=username, password=get_hash(password))
        else:
            obj = self.get_one_object(username=username)
        '''
        # 解决登录bug代码
        if password is None:
            # 根据用户名来查找账户信息
            obj = self.get_one_object(username=username)
        else:
            # 根据用户名和密码来查找账户信息
            obj = self.get_one_object(username=username, password=get_hash(password))
        return obj


class Passport(BaseModel):
    '''
    账户类
    '''
    username = models.CharField(max_length=20, help_text='用户名')
    password = models.CharField(max_length=40, help_text='密码')
    nikename = models.CharField(max_length=20, help_text='昵称')

    '''
    def __init__(self, username, password, email):
        self.username = username
        self.password = password
        self.email = email
    '''

    # 创建一个自定义模型管理器的对象
    objects = PassportManager()

    class Meta:
        db_table = 'python_sys_user'