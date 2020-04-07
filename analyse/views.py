import json
import os
import re

import onnx
from django.http import HttpResponse, HttpResponseNotFound
from django.shortcuts import render
import analyse.analyse


# Create your views here.
def home(request):
    return render(request, "analyse.html")


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


def getparm(request):
    path = model_path()
    if path == '':
        print('file Not Found')
    dic = analyse.analyse.analyze(onnx.load(path))

    if request.method == 'POST':
        js = {
            'getparm': {
                'category': [l[0] for l in dic['layers']],
                'data': [l[1] for l in dic['layers']]
            },
            's_layers_num': [
                {'value': dic['conv_cnt'], 'name': '卷积层'},
                {'value': dic['fc_cnt'], 'name': '全连接层'},
            ],
            's_layers_size': [
                {'value': dic['conv_param_cnt'], 'name': '卷积层'},
                {'value': dic['fc_param_cnt'], 'name': '全连接层'},
            ]
        }
        return HttpResponse(json.dumps(js), content_type="application/json")
    return HttpResponseNotFound()


def run_time(request):
    if request.method == 'POST':
        tim = list(range(24))
        fp = [1300 - 50 * i for i in tim]
        quant = [650 - 25 * i for i in tim]
        js = {
            'category': tim,
            'fp': fp,
            'quant': quant
        }
        return HttpResponse(json.dumps(js), content_type="application/json")
    return HttpResponseNotFound()
