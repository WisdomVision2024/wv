
from django.shortcuts import render
from .models import *
from rest_framework import viewsets
from .serializers import *
from django.http import HttpResponse
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import io
import socket
import os
from time import sleep
import cv2
import numpy as np
from collections import Counter
import select
import app.socketclient as socketclient
from . import recordquestion
from django.shortcuts import redirect
from . import question_input
import logging
# 設定 logging 格式
logging.basicConfig(format='%(asctime)s - %(message)s - [%(funcName)s:%(lineno)d]', level=logging.DEBUG)



class userdataViewSet(viewsets.ModelViewSet): 
    #ModelViewSet提供了處理模型的完整 CRUD（創建、讀取、更新、刪除）操作的默認實現
    queryset = userdata.objects.all()
    #指定視圖集應該操作的模型實例集,意味著UserViewSet 將處理所有User模型的實例
    serializer_class = userdataSerializer
    #UserViewSet 將使用 UserSerializer 類來序列化和反序列化User模型實例

#登入
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

#註冊
@csrf_exempt
def register_view(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        cPhone = data.get('Phone')
        cPassword = data.get('Password')
        cName = data.get('Name')
        cEmail = data.get('Email')
        cIdentity = data.get('Identity')


        register_result = register_user(cPhone,cPassword,cName,cEmail,cIdentity)

        return JsonResponse(register_result)
    else:
        return JsonResponse({"error": "只接受 POST 请求"})
    

#前端丟入continue語音模型
@csrf_exempt
def focus_view(request):
    if request.method != 'POST':
        return JsonResponse({"error": "只接受 POST 请求"})

    # 嘗試解析 JSON 數據
    d = json.loads(request.body)
    data = d.get('key')
    # 處理數據的邏輯...
    r = ("正在幫您關注"+recordquestion.look(data))

    return JsonResponse({'status': 'success','message':r},safe=False)

#前端丟入連續物品辨識模型
@csrf_exempt
def continue_view(request):
    # 檢查請求方法是否為 POST，且請求中是否包含文件
    if request.method == 'POST' and 'file' in request.FILES:
        # 取得上傳的文件
        uploaded_file = request.FILES['file']
        try:
            # 讀取文件數據並將其轉換為 numpy 陣列
            img_array = np.frombuffer(uploaded_file.read(), np.uint8)
            # 使用 OpenCV 解碼 numpy 陣列為圖像
            frame = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

            # 如果圖像解碼失敗，返回錯誤響應
            if frame is None:
                return JsonResponse({"status": "error", "message": "Image decoding failed."}, status=500)

            # 將圖像編碼為 JPEG 格式的字節數據
            success, img_encoded = cv2.imencode('.jpg', frame)
            # 如果編碼失敗，返回錯誤響應
            if not success:
                return JsonResponse({"status": "error", "message": "Image encoding failed"}, status=500)
            
            # 將編碼的圖像數據轉換為字節串
            data = img_encoded.tobytes()
            # 添加結束標誌
            data += b'EOF'
            print(f"Size of encoded image data: {len(data)} bytes")
            
            r1 = socketclient.sock1(data)
            r2 = socketclient.sock2(data)

            result = r1+r2

            return JsonResponse({"status": "success","message":result},status=200)

        except Exception as e:
            # 處理過程中可能出現的錯誤，返回錯誤響應
            return JsonResponse({"status": "error", "message": str(e)}, status=500)
    else:
        # 如果請求方法不是 POST 或沒有文件，返回錯誤響應
        return JsonResponse({"status": "error", "message": "Invalid request."}, status=400)

@csrf_exempt
def help_view(request):
    if request.method == 'POST' and 'file' in request.FILES:
        
        uploaded_file = request.FILES['file']
        # 讀取文件數據並將其轉換為 numpy 陣列
        img_array = np.frombuffer(uploaded_file.read(), np.uint8)
        # 使用 OpenCV 解碼 numpy 陣列為圖像
        frame = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
        # 如果圖像解碼失敗，返回錯誤響應
        if frame is None:
            return JsonResponse({"status": "error", "message": "Image decoding failed."}, status=500)
        # 將圖像編碼為 JPEG 格式的字節數據
        success, img_encoded = cv2.imencode('.jpg', frame)
        # 如果編碼失敗，返回錯誤響應
        if not success:
            return JsonResponse({"status": "error", "message": "Image encoding failed"}, status=500)
        
        # 將編碼的圖像數據轉換為字節串
        data = img_encoded.tobytes()
        # 添加結束標誌
        data += b'EOF'
        print(f"Size of encoded image data: {len(data)} bytes")

        r3 = socketclient.sock3(data)
        encoded_str = json.loads(r3)
        print(encoded_str)

        with open('unity.txt', 'w') as file:
            for item in encoded_str:
                file.write(str(item) + '\n')  # 每個元素轉換為字符串後單獨寫入一行
            # file.write(json.dumps(encoded_str))  # 覆蓋寫入新內容
        # if encoded_str is not None:
        #     # 存储数据到 session
        #     request.session['param'] = encoded_str
    
            # 重定向到目标视图
        return redirect('unity_view')
     # 如果不是 POST 請求或沒有文件，返回一個錯誤響應
    return JsonResponse({"status": "error", "message": "Invalid request. No file uploaded."}, status=400)   
     

#前端丟入物品辨識模型
@csrf_exempt
def object_view(request):
    # 檢查請求方法是否為 POST，且請求中是否包含文件
    if request.method == 'POST' and 'file' in request.FILES:
        # 取得上傳的文件
        uploaded_file = request.FILES['file']
        try:
            # 讀取文件數據並將其轉換為 numpy 陣列
            img_array = np.frombuffer(uploaded_file.read(), np.uint8)
            # 使用 OpenCV 解碼 numpy 陣列為圖像
            frame = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

            # 如果圖像解碼失敗，返回錯誤響應
            if frame is None:
                return JsonResponse({"status": "error", "message": "Image decoding failed."}, status=500)

            # 將圖像編碼為 JPEG 格式的字節數據
            success, img_encoded = cv2.imencode('.jpg', frame)
            # 如果編碼失敗，返回錯誤響應
            if not success:
                return JsonResponse({"status": "error", "message": "Image encoding failed"}, status=500)
            
            # 將編碼的圖像數據轉換為字節串
            data = img_encoded.tobytes()
            # 添加結束標誌
            data += b'EOF'
            print(f"Size of encoded image data: {len(data)} bytes")
            socketclient.sock1(data)
            socketclient.sock2(data)
           
            return JsonResponse({"status": "success"})

        except Exception as e:
            # 處理過程中可能出現的錯誤，返回錯誤響應
            return JsonResponse({"status": "error", "message": str(e)}, status=500)
    else:
        # 如果請求方法不是 POST 或沒有文件，返回錯誤響應
        return JsonResponse({"status": "error", "message": "Invalid request."}, status=400)
#前端丟入語音模型
@csrf_exempt
def gemini_view(request):
    if request.method != 'POST':
        return JsonResponse({"error": "只接受 POST 请求"})

    # 嘗試解析 JSON 數據
    d = json.loads(request.body)
    data = d.get('key')
    # 處理數據的邏輯...
    q = question_input.Objection().ask(data)

    return JsonResponse({'status': 'success','message':q},safe=False)

            
#to_unity
@csrf_exempt
def unity_view(request):
    if request.method == 'GET':
        with open('unity.txt', 'r', encoding='utf-8') as file:
            content = file.read()
       
      # 从 session 中获取数据
        # param = request.session.get('param', 'befault_value')


    #  # 清理 session 中的数据（可选）
    #     if 'param' in request.session:
    #         del request.session['param']
    
    # 处理参数
    # response_data = {'status': 'success', 'param': param}
        return HttpResponse(content)

@csrf_exempt
def unity2_view(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        # if received_string is not None:
        #     # 存储数据到 session
        #     request.session['q'] = received_string
        #     # 重定向到目标视图
        # return redirect('get_unity')
        with open('get_unity.txt', 'w') as file:
             file.write(json.dumps(data))
        return JsonResponse({"status": data}, status=200)

    else:
        return JsonResponse({"error": "只接受 POST 請求"}, status=405)
    

@csrf_exempt
def get_unity(request):
    if request.method == 'GET':
        with open('get_unity.txt', 'r', encoding='utf-8') as file:
            content = file.read()
        # 处理参数
        response_data = {'status': 'success', 'param':content}
        return JsonResponse(response_data)








    


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


