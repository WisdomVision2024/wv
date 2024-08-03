
from django.shortcuts import render
from .models import *
from rest_framework import viewsets,status
from .serializers import *
from django.http import HttpResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from yuno import gemini
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from PIL import Image
import io



class userdataViewSet(viewsets.ModelViewSet): 
    #ModelViewSet提供了處理模型的完整 CRUD（創建、讀取、更新、刪除）操作的默認實現
    queryset = userdata.objects.all()
    #指定視圖集應該操作的模型實例集,意味著UserViewSet 將處理所有User模型的實例
    serializer_class = userdataSerializer
    #UserViewSet 將使用 UserSerializer 類來序列化和反序列化User模型實例


@csrf_exempt
def login_view(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        Phone = data.get('Phone')
        Password = data.get('Password')

        #Phone = request.POST.get('Phone')
        #Password = request.POST.get('Password')
        
        login_result = login_user(Phone, Password)

        return JsonResponse(login_result)
    else:
        return JsonResponse({"error": "只接受 POST 请求"})

@csrf_exempt
def register_view(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        cPhone = data.get('Phone')
        cPassword = data.get('Password')
        cName = data.get('Name')
        cEmail = data.get('Email')
        cIdentity = data.get('Identity')

        #cPhone = request.POST.get('Phone')
        #cPassword = request.POST.get('Password')
        #cName = request.POST.get('Name')
        #cEmail = request.POST.get('Email')
        #cIdentity = request.POST.get('Identity')

        register_result = register_user(cPhone,cPassword,cName,cEmail,cIdentity)

        return JsonResponse(register_result)
    else:
        return JsonResponse({"error": "只接受 POST 请求"})


@csrf_exempt
def gemini_view(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        T = data.get('T')
        result = gemini.Gemini.get_gemini(T)
        return JsonResponse(result)
    else:
        return JsonResponse({"error": "只接受 POST 请求"})



@api_view(['GET'])
def unity_view(request):
    data = {
        "position": {
            "x": 1,
            "y": 2,
            "z": 3
        }

    }
    return Response(data)


@api_view(['POST'])
def bytearray(request): 
    global global_byte_data
    # 获取原始字节数据
    global_byte_data = "request.body"
    return Response({"status": "success", "message": "Byte data received"})

   

@api_view(['GET'])
def bytearrayget(request):
    data = global_byte_data
    if data is not None:
        return Response(data, content_type='application/octet-stream')
    else:
        return Response({"status": "error", "message": "No byte data found"}, status=404)




import requests
def login1(request):
    return render(request, 'login1.html')


def login2(request): 
    api_url = 'http://163.13.201.104:8080/login/'
    response = requests.post(api_url,data=request.POST) 
    data = response.json()
    return render(request, 'login2.html',{'data':data})


def signup1(request):
    return render(request,'signup1.html')


def signup2(request):
    api_url = 'http://163.13.201.104:8080/signup/'
    response = requests.post(api_url,data=request.POST) 
    data = response.json()
    return render(request, 'signup2.html',{'data':data})


def hello(request):
 
    return HttpResponse("Hello Django!")


