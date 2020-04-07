import json
import os

import onnx
from django.http import HttpResponse, HttpResponseNotFound, FileResponse
from django.shortcuts import render
import newdj.settings
from analyse import analyse
import threading
import datetime

# 执行具体任务的异步线程
class TaskThread(threading.Thread):
    def run(self):
        import time

        for i in range(20):
            time.sleep(1)
            print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),"%s" % (self.getName(),))


def CreateTask(request):
    taskThread = TaskThread()
    taskThread.start()
    # testThread.join() # 如果加上就会等线程执行完才响应，在我们这个场景下不加
    return HttpResponse(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

# Cr# eate your views here.
def home(request):
    return render(request, 'deploy.html')


def set_platform(request):
    if request.method == 'POST':
        plat = request.POST.get('platform')
        print("set platform to " + plat)
        return HttpResponse(plat)
    return HttpResponseNotFound()


def get_target_file(request):
    f = os.path.join(newdj.settings.BASE_DIR, 'upload', 'tem')
    ls = os.listdir(f)
    return FileResponse(open(os.path.join(f, ls[0]), 'rb'))


def get_basic_info(request):
    f = os.path.join(newdj.settings.BASE_DIR, 'upload', 'tem')
    ls = os.listdir(f)
    p = os.path.join(f, ls[0])
    basic = analyse.get_basic_info(onnx.load(p))
    with open(p, 'rb') as f:
        js = {
            'name': f.name,
            'size': os.path.getsize(p) / 1024.0 / 1024.0,
            'layer_num': basic['layer_num'] - 2,
            'din': str(basic['din']),
            'dout': str(basic['dout'])
        }
        return HttpResponse(json.dumps(js), content_type="application/json")