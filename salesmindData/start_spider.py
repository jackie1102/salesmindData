from conf import *
from spider.models import *
import json
from utils.spider_dict import *
import time
import asyncio


run_task_id_1 = []
run_task_id_2 = []


async def start_task1():
    while True:
        try:
            tasks = SpiderTask.objects.get_object_list({'status_1': 1, 'is_delete': 0})
        except:
            continue
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
                    print(str(E))
        await asyncio.sleep(5)


async def start_task2():
    while True:
        try:
            tasks = SpiderTask.objects.get_object_list({'status_2': 1, 'is_delete': 0})
        except:
            continue
        for task in tasks:
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
        await asyncio.sleep(5)


async def auto_start_task2():
    while True:
        now_tim = int(time.time())
        start_tim = now_tim - 24 * 60 * 60
        modified_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(start_tim))
        try:
            obj_list = SpiderTask.objects.get_object_list(filters={'status_1': 2, 'status_2': 0, 'update_time__gt': modified_time, 'is_delete': 0})
        except:
            continue
        for task in obj_list:
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
        await asyncio.sleep(5)


async def change_runtask_id1():
    while True:
        try:
            objs = SpiderTask.objects.get_object_list({'id__in': run_task_id_1})
        except:
            continue
        for obj in objs:
            if obj.status_1 != 1:
                run_task_id_1.remove(obj.id)
        await asyncio.sleep(5)


async def change_runtask_id2():
    while True:
        try:
            objs = SpiderTask.objects.get_object_list({'id__in': run_task_id_2})
        except:
            continue
        for obj in objs:
            if obj.status_2 != 1:
                run_task_id_2.remove(obj.id)
        await asyncio.sleep(5)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    tasks = [
        asyncio.ensure_future(start_task1()),
        asyncio.ensure_future(start_task2()),
        asyncio.ensure_future(auto_start_task2()),
        asyncio.ensure_future(change_runtask_id1()),
        asyncio.ensure_future(change_runtask_id2()),
    ]
    asyncio.gather(*tasks)
    loop.run_forever()