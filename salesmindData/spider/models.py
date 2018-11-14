import json
import time
from django.db import models
from db.base_model import BaseModel
from db.base_manager import BaseModelManager
from utils.utils import USER_NAME


class SpiderTaskManage(BaseModelManager):

    def start_task1(self, task_id):
        task = self.get_one_object(id=task_id)
        if task:
            task.status_1 = 1
            while True:
                try:
                    task.save()
                    break
                except:
                    pass

    def start_task2(self, task_id):
        task = self.get_one_object(id=task_id)
        if task:
            task.status_2 = 1
            while True:
                try:
                    task.save()
                    break
                except:
                    pass

    def finish_task1(self, task_id):
        task = self.get_one_object(id=task_id)
        if task:
            task.status_1 = 2
            while True:
                try:
                    task.save()
                    break
                except:
                    pass

    def finish_task2(self, task_id):
        task = self.get_one_object(id=task_id)
        if task:
            task.status_2 = 2
            while True:
                try:
                    task.save()
                    break
                except:
                    pass

    def change_task1_status(self, task_id):
        task = self.get_one_object(id=task_id)
        if task:
            task.status_1 = 3
            while True:
                try:
                    task.save()
                    break
                except:
                    pass

    def change_task2_status(self, task_id):
        task = self.get_one_object(id=task_id)
        if task:
            task.status_2 = 3
            while True:
                try:
                    task.save()
                    break
                except:
                    pass

    def get_one_task(self, **filters):
        obj = self.get_one_object(**filters)
        return obj

    def add_one_task(self, table_name, user_id, spider_id, param):
        '''
        添加一个爬虫任务
        '''
        obj = self.get_one_object(table_name=table_name)
        if obj:
            obj = None
        else:
            obj = self.create_one_object(table_name=table_name, user_id=user_id, spider_id=spider_id, param=param,
                                         data_totle=0)
        return obj

    def get_task_list_by_user_id(self, user_id, create_time):
        '''
        根据用户id查询任务列表
        '''
        now_tim = int(time.time())
        if create_time != '不限':
            start_tim = now_tim - int(create_time) * 24 * 60 * 60
            modified_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(start_tim))
            if user_id == '0':
                obj_list = self.get_object_list(filters={'update_time__gt': modified_time, 'is_delete': 0})
            else:
                obj_list = self.get_object_list(
                    filters={'user_id': int(user_id), 'update_time__gt': modified_time, 'is_delete': 0})
        else:
            if user_id == '0':
                obj_list = self.get_object_list(filters={'is_delete': 0})
            else:
                obj_list = self.get_object_list(filters={'user_id': int(user_id), 'is_delete': 0})
        task_list = []
        for obj in obj_list:
            task = {}
            task["task_id"] = obj.id
            task['user'] = USER_NAME.get(str(obj.user_id))
            task['spider_id'] = obj.spider_id
            task["table_name"] = json.loads(obj.param).get("table_name")
            task["start_time"] = str(obj.create_time).split('.')[0]
            task["totle_count"] = obj.data_totle
            try:
                count = task["totle_count"] - SpiderData.objects.get_data_count_by_taskid(task_id=obj.id)
                task["progress"] = int(count * 100 / obj.data_totle)
            except:
                task["progress"] = 0
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
            if obj.download_status == 0:
                task['download_status'] = '下载'
            else:
                task['download_status'] = '已下载'
            task_list.append(task)
        return task_list


class SpiderDataManage(BaseModelManager):

    def get_data_count_by_taskid(self, task_id):
        count = self.get_object_list(filters={'data_task_id': task_id}).count()
        return count

    def del_one_data(self, data_id):
        obj = self.get_one_object(id=data_id)
        if obj:
            while True:
                try:
                    obj.delete()
                    break
                except:
                    pass

    def add_data_list(self, data_list, task_id):
        cls = self.model
        querysetlist = [cls(data=data, data_task_id=task_id) for data in data_list]
        cls.objects.bulk_create(querysetlist)

    def get_data_list_by_task_id(self, task_id):
        obj_list = self.get_object_list(filters={'data_task_id': task_id})
        data_list = []
        for obj in obj_list:
            data = obj.data
            data_id = obj.id
            data_list.append({'id': data_id, 'data': data})
        return data_list


class ZhiLianIdManage(BaseModelManager):

    def get_one_ID_by_id(self, data_id):
        obj = self.get_one_object(id=data_id)
        return obj

    def get_one_ID_by_task_id(self, task_id):
        obj = self.get_one_object(task_id=task_id)
        return obj

    def get_data_list_by_status(self, status):
        obj_list = self.get_object_list(filters={'status': status})
        return obj_list


class JobIdManage(BaseModelManager):

    def get_one_ID_by_id(self, data_id):
        obj = self.get_one_object(id=data_id)
        return obj

    def get_one_ID_by_task_id(self, task_id):
        obj = self.get_one_object(task_id=task_id)
        return obj

    def get_data_list_by_status(self, status):
        obj_list = self.get_object_list(filters={'status': status})
        return obj_list


class SpiderTask(BaseModel):
    spider_id = models.CharField(max_length=30, help_text='爬虫id')
    table_name = models.CharField(max_length=40, help_text='下载表名')
    status_1 = models.IntegerField(default=0, help_text='运行状态1')
    status_2 = models.IntegerField(default=0, help_text='运行状态2')
    user_id = models.IntegerField(help_text='用户id')
    param = models.TextField(help_text='配置参数')
    data_totle = models.IntegerField(default=0, help_text="data总数")
    progress = models.IntegerField(default=0, help_text="已经爬取data数量百分比")
    download_status = models.IntegerField(default=0, help_text='下载状态')

    objects = SpiderTaskManage()

    class Meta:
        db_table = 'python_task'


class SpiderData(BaseModel):
    data = models.TextField(help_text='待抓取的url或者公司')
    data_task = models.ForeignKey('SpiderTask')

    objects = SpiderDataManage()

    class Meta:
        db_table = 'task_data'


class ZhiLianId(BaseModel):
    username = models.CharField(max_length=30, help_text='用户名')
    password = models.CharField(max_length=40, help_text='密码')
    status = models.IntegerField(default=0, help_text='是否被占用')
    task_id = models.IntegerField(default=0, help_text='占用任务ID')

    objects = ZhiLianIdManage()

    class Meta:
        db_table = 'ZhiLianUser'


class JobId(BaseModel):
    vipname = models.CharField(max_length=30, help_text='会员名称')
    username = models.CharField(max_length=30, help_text='用户名')
    password = models.CharField(max_length=40, help_text='密码')
    status = models.IntegerField(default=0, help_text='是否被占用')
    task_id = models.IntegerField(default=0, help_text='占用任务ID')

    objects = JobIdManage()

    class Meta:
        db_table = 'JobUser'
