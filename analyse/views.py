import json
from django.http import HttpResponse, HttpResponseNotFound
from django.shortcuts import render


# Create your views here.
def home(request):
    return render(request, "analyse.html")


def getparm(request):
    if request.method == 'POST':
        js = {
            'category': ['conv[0]', 'conv[1]', 'conv[2]', 'conv[3]', 'conv[4]', 'conv[5]', 'conv[6]', 'conv[7]', 'conv[8]', 'conv[9]', 'conv[10]', 'conv[11]', 'conv[12]', 'conv[13]', 'conv[14]', 'conv[15]', 'conv[16]', 'conv[17]', 'conv[18]', 'conv[19]', 'fc[0]'],
            'data': [37,147,147,147,147,294
    ,589
    ,32
    ,589
    ,589
    ,1179
    ,2359
    ,131
    ,2359
    ,2359
    ,4718
    ,9437
    ,524
    ,9437
    ,9437
    ,2052]
        }
        return HttpResponse(json.dumps(js), content_type="application/json")
    return HttpResponseNotFound()


def s_layers_num(request):
    if request.method == 'POST':
        js = [
            {'value': 20, 'name': '卷积层'},
            {'value': 1, 'name': '全连接层'},
              ]
        return HttpResponse(json.dumps(js), content_type="application/json")
    return HttpResponseNotFound()


def s_layers_size(request):
    if request.method == 'POST':
        js = [
            {'value': 40086, 'name': '卷积层'},
            {'value': 2025, 'name': '全连接层'},
        ]
        return HttpResponse(json.dumps(js), content_type="application/json")
    return HttpResponseNotFound()


def run_time(request):
    if request.method == 'POST':
        tim = list(range(24))
        print(tim)
        fp = [1300 - 50 * i for i in tim]
        quant = [650 - 25 * i for i in tim]
        js = {
            'category': tim,
            'fp': fp,
            'quant': quant
        }
        return HttpResponse(json.dumps(js), content_type="application/json")
    return HttpResponseNotFound()