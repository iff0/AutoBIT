import os

from django.http import HttpResponse, HttpResponseNotFound, FileResponse
from django.shortcuts import render
import newdj.settings


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
    f = open(os.path.join(f, ls[0]), 'rb')
    fr = FileResponse(f)
    return fr
