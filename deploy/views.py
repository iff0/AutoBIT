import json
import os
import subprocess
import queue

import onnx
import re
from django.http import HttpResponse, HttpResponseNotFound, FileResponse
from django.shortcuts import render
import newdj.settings
from analyse import analyse
import threading
import datetime

output_list = queue.Queue()
target = 'cuda'
target_dic = {
    'Nivida GPU':'cuda',
    'FPGA': 'llvm',
    'Pi 4B': 'llvm'
}

def rundeploy(module_path, target, quantize, tune, rpc):
    print("Deploy running...")
    pyFileName = 'deploy/deploy.py'
    quantize_flag = 'quantize' if quantize else 'noquantize'
    tune_flag = 'tune' if tune else 'notune'
    rpc_flag = 'rpc' if rpc else 'norpc'
    command = r'python -u %s %s %s %s %s' % (pyFileName, module_path, target, quantize_flag, tune_flag)
    getOutPut = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, bufsize=1)
    while getOutPut.poll() is None:
        line = getOutPut.stdout.readline()
        if line:
            print(line)
            output_list.put(str(line, encoding = "utf-8").replace('\n', ''))
    lines = getOutPut.communicate()[0]
    if lines:
        for line in lines:
            print(str(line))
            output_list.put(str(line, encoding = "utf-8").replace('\n', ''))


# 执行具体任务的异步线程
class TaskThread(threading.Thread):
    def __init__(self, target='cuda',quantize=False, tune=False, rpc=False):
        threading.Thread.__init__(self)
        self.target = target
        self.quantize = quantize
        self.tune = tune
        self.rpc = rpc


    def run(self):
        import time

        # from deploy.deploy import run_deploy
        modelPath = model_path()
        print(modelPath)
        rundeploy(modelPath, target, self.quantize, self.tune, self.rpc)


def model_path():
    p = 'upload/tem/'
    path = ''
    ls = os.listdir(p)
    for l in ls:
        if re.match(r'(.*\.onnx)', l):
            path = os.path.join(p, l)
            return path
    # 找模型文件
    return path

def renew_output(request):
    line = ''
    if output_list.empty():
        return HttpResponse(line)
    line = output_list.get()
    return HttpResponse(line)


def lanuch_deploy(request):
    if request.method == 'POST':
        if_q = request.POST.get("if_quantization")
        if_tune = request.POST.get("if_tune")
        if_rpc: object = request.POST.get("if_rpc")
        if_q = True if if_q == 1 else False
        if_tune = True if if_tune == 1 else False
        if_rpc = True if if_rpc == 1 else False
        print(if_q)
        print(if_tune)
        print(if_rpc)

        # 0 or 1 for false and true
        plat = request.POST.get('platform')
        print(plat)
        print("lanuching deploy..")
        taskThread = TaskThread(if_q,if_tune,if_rpc)
        taskThread.start()
        return HttpResponse()
    return HttpResponseNotFound()
# Cr# eate your views here.
def home(request):
    return render(request, 'deploy.html')


#def set_platform(request):
 #   if request.method == 'POST':
  #      plat = request.POST.get('platform')
   #     global target
    #    target = target_dic[plat]
     #   print("set platform to " + plat + ' based on ' + target)
      #  return HttpResponse(plat)
    #return HttpResponseNotFound()


def get_target_file(request):
    f = os.path.join(newdj.settings.BASE_DIR, 'download', 'tem')
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