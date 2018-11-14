from conf import *
from spider.models import *
import json
from utils.spider_dict import *
import time


run_task_id_1 = []
run_task_id_2 = []


def start_task1():
    while True:
        tasks = SpiderTask.objects.get_object_list({'status_1': 1, 'is_delete': 0})
        for task in tasks:
            task_id = task.id
            spider_id = task.spider_id
            if task.id not in run_task_id_1:
                param = json.loads(task.param)
                param['task_id'] = task_id
                try:
                    spider = TaskCode1.get(str(spider_id))(param)
                    t1 = threading.Thread(target=spider.run)
                    t2 = threading.Thread(target=spider.change_sign_status_1)
                    t1.start()
                    t2.start()
                    run_task_id_1.append(task.id)
                except Exception as E:
                    print(E)
        time.sleep(5)


def start_task2():
    while True:
        tasks = SpiderTask.objects.get_object_list({'status_2': 1, 'is_delete': 0})
        for task in tasks:
            lock.acquire()
            if task.id not in run_task_id_2:
                param = json.loads(task.param)
                param['task_id'] = task.id
                try:
                    spider = TaskCode2.get(str(task.spider_id))(param)
                    t1 = threading.Thread(target=spider.run)
                    t2 = threading.Thread(target=spider.change_sign_status_2)
                    t1.start()
                    t2.start()
                    run_task_id_2.append(task.id)
                except Exception as E:
                    print(str(E))
            lock.release()
        time.sleep(5)


def auto_start_task2():
    while True:
        now_tim = int(time.time())
        start_tim = now_tim - 24 * 60 * 60
        modified_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(start_tim))
        obj_list = SpiderTask.objects.get_object_list(filters={'status_1': 2, 'status_2': 0, 'update_time__gt': modified_time, 'is_delete': 0})
        for task in obj_list:
            lock.acquire()
            if task.id not in run_task_id_2:
                try:
                    param = json.loads(task.param)
                    param['task_id'] = task.id
                    spider = TaskCode2.get(str(task.spider_id))(param)
                    t1 = threading.Thread(target=spider.run)
                    t2 = threading.Thread(target=spider.change_sign_status_2)
                    t1.start()
                    t2.start()
                    run_task_id_2.append(task.id)
                    SpiderTask.objects.start_task2(task_id=task.id)
                except Exception as E:
                    print(E)
            lock.release()
        time.sleep(5)


def change_runtask_id1():
    while True:
        objs = SpiderTask.objects.get_object_list({'id__in': run_task_id_1})
        for obj in objs:
            if obj.status_1 != 1:
                run_task_id_1.remove(obj.id)
        time.sleep(5)


def change_runtask_id2():
    while True:
        objs = SpiderTask.objects.get_object_list({'id__in': run_task_id_2})
        for obj in objs:
            if obj.status_2 != 1:
                run_task_id_2.remove(obj.id)
        time.sleep(5)


if __name__ == '__main__':
    thread_list = [
        threading.Thread(target=start_task1),
        threading.Thread(target=start_task2),
        threading.Thread(target=auto_start_task2),
        threading.Thread(target=change_runtask_id1),
        threading.Thread(target=change_runtask_id2)
        ]
    for thread in thread_list:
        thread.start()
    for thread in thread_list:
        thread.join()

