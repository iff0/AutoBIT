import os
import re

from django.http import HttpResponse, HttpResponseNotFound
from django.shortcuts import render

from . import tool
from newdj import settings


# 起始页面
# onload的get请求，映射到第一个网页
def home(request):
    return render(request, "index.html")


# 测试页面
# 用于测试/debug
def test(request):
    return render(request, "test.html")


# 文件上传请求，post
def upload_model(request):
    if request.method == 'POST':
        f = request.FILES.get('my_model')
        # 取文件
        if f is None:
            print("What is the browser side doing?")
            return HttpResponseNotFound("404 Error")
        # 是否无文件
        print('We got a file named ' + str(f.name) + ' with size of ' + str(f.size) + ' b')
        path = os.path.join(settings.BASE_DIR, 'upload', 'tem')
        # 文件缓存目录'upload/tem/',每次加入前清空缓存
        ls = os.listdir(path)
        for l in ls:
            os.remove(os.path.join(path, l))
        # 确定写目录
        path = os.path.join(path, f.name)
        # 用django 的 chunk以防文件过大卡了
        with open(path, "wb") as tf:
            for chunk in f.chunks():
                tf.write(chunk)
        return HttpResponse("你的文件 " + str(f.name) + " 已上传", content_type="text/plain")
    return HttpResponseNotFound("404 Error")


# 结构可视化请求, get
def structure_view(requset):
    p = 'upload/tem/'
    path = ''
    ls = os.listdir(p)
    for l in ls:
        if re.match(r'(.*\.onnx)', l):
            path = os.path.join(p, l)
            break
    # 找模型文件
    if path == '':
        print('wtf where is my model?')
        return HttpResponseNotFound('404 Error')
    port = 8080
    # 在端口8080开本地服务
    tool.net_see(path, port)
    return HttpResponse('http://localhost:' + str(port) + '/')
