
from django.shortcuts import render
from .models import *
from rest_framework import viewsets
from .serializers import *
from django.http import HttpResponse
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import cv2
import numpy as np
import app.socketclient as socketclient
from . import recordquestion
from django.shortcuts import redirect
from . import question_input
import logging
import os
# 設定 logging 格式
logging.basicConfig(format='%(asctime)s - %(message)s - [%(funcName)s:%(lineno)d]', level=logging.DEBUG)

import threading
# 全局變量來控制中斷
break_signal = threading.Event()

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
#更改帳號   
@csrf_exempt
def update_view(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        Phone = data.get('Phone')  # 使用者電話號碼
        newName = data.get('newName')  # 新的名稱
        newEmail = data.get('newEmail')  # 新的電子郵件
        oldPassword = data.get('oldPassword')  # 舊的密碼
        newPassword = data.get('newPassword')  # 新的密碼
        
        # 更新使用者帳號資訊的邏輯
        update_result = update_account(Phone,newName, newEmail, oldPassword,newPassword)

        return JsonResponse(update_result)
    else:
        return JsonResponse({"error": "只接受 POST 请求"})
    
@csrf_exempt
def update_image(request):
    if request.method == 'POST' and 'file' in request.FILES and 'filename' in request.POST:
        # 取得上傳的文件
        uploaded_file = request.FILES['file']
        
        # 從 POST 資料中取得客戶端傳來的圖片名稱
        client_filename = request.POST['filename']

         # 確保文件名有正確的擴展名
        valid_extensions = ['.jpg', '.jpeg', '.png']
        if not any(client_filename.lower().endswith(ext) for ext in valid_extensions):
            client_filename += '.jpg'  # 如果沒有擴展名，默認添加 '.jpg'

        
        # 讀取文件數據並將其轉換為 numpy 陣列
        img_array = np.frombuffer(uploaded_file.read(), np.uint8)
        
        # 使用 OpenCV 解碼 numpy 陣列為圖像
        frame = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
        
        # 指定儲存圖片的資料夾
        save_directory = '/home/tkuim-sd/wv/media/image/'
        
        # 檢查資料夾是否存在，不存在則創建
        if not os.path.exists(save_directory):
            os.makedirs(save_directory)
        
        # 完整的文件路徑，使用客戶端傳送的文件名
        save_path = os.path.join(save_directory, client_filename)
        
        # 保存圖片
        cv2.imwrite(save_path, frame)
        
        return JsonResponse({"status": "OK"})
    else:
        return JsonResponse({"status": "只接受 POST 請求，並需要包含文件和文件名"})
    

#前端丟入continue語音模型
@csrf_exempt
def focus_view(request):
    if request.method != 'POST':
        return JsonResponse({"error": "只接受 POST 请求"})
     # 觸發中斷信號
    break_signal.set()

    # 重置中斷信號，為下一次使用做好準備
    break_signal.clear()
    # 嘗試解析 JSON 數據
    d = json.loads(request.body)
    data = d.get('T')
    # 處理數據的邏輯...
    r = ("正在幫您關注"+recordquestion.look(data))

    return JsonResponse({'status': 'success','message':r},safe=False)

from . import object_continue
from . import face_continue
#前端丟入連續物品辨識模型

# 定義執行緒處理模型 1 的函數
def process_model_1(data, result):
    r1 = socketclient.sock1(data)
    if r1 is not None:
        result['d1'] = object_continue.con(r1)
    else:
        result['d1'] = " "

# 定義執行緒處理模型 2 的函數
def process_model_2(data, result):
    r2 = socketclient.sock2(data)
    if r2 is not None:
        result['d2'] = face_continue.facecon(r2)
    else:
        result['d2'] = " "

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
            cv2.imwrite('/home/tkuim-sd/image2/image.jpg', frame)

            # 將圖像編碼為 JPEG 格式的字節數據
            success, img_encoded = cv2.imencode('.jpg', frame)
            if not success:
                return JsonResponse({"status": "error", "message": "Image encoding failed"}, status=500)
            
            # 將編碼的圖像數據轉換為字節串
            data = img_encoded.tobytes()
            data += b'EOF'
            print(f"Size of encoded image data: {len(data)} bytes")

            # 建立一個用於儲存模型結果的字典
            result = {}

            # 啟動執行緒以並行處理兩個模型
            thread1 = threading.Thread(target=process_model_1, args=(data, result))
            thread2 = threading.Thread(target=process_model_2, args=(data, result))

            # 啟動執行緒
            thread1.start()
            thread2.start()

            # 等待兩個執行緒完成
            thread1.join()
            thread2.join()

            # 將兩個模型的結果組合
            d1 = result.get('d1', " ")
            d2 = result.get('d2', " ")
            final_result = d1 + d2
            return JsonResponse({"status": "success", "message": final_result}, status=200)

        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=500)
    else:
        return JsonResponse({"status": "error", "message": "Invalid request."}, status=400)
    



import threading

def send_to_model_1(data):
    socketclient.sock1(data)

def send_to_model_2(data):
    socketclient.sock2(data)

def send_to_model_3(data):
    socketclient.sock3(data)
@csrf_exempt
def object_view(request):
    if request.method == 'POST' and 'file' in request.FILES:
        uploaded_file = request.FILES['file']
        try:
            img_array = np.frombuffer(uploaded_file.read(), np.uint8)
            frame = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

            if frame is None:# def continue_view(request):
#     # 檢查請求方法是否為 POST，且請求中是否包含文件
#     if request.method == 'POST' and 'file' in request.FILES:
#         # 取得上傳的文件
#         uploaded_file = request.FILES['file']
#         try:
#             # 讀取文件數據並將其轉換為 numpy 陣列
#             img_array = np.frombuffer(uploaded_file.read(), np.uint8)
#             # 使用 OpenCV 解碼 numpy 陣列為圖像
#             frame = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

#             # 如果圖像解碼失敗，返回錯誤響應
#             if frame is None:
#                 return JsonResponse({"status": "error", "message": "Image decoding failed."}, status=500)

#             # 將圖像編碼為 JPEG 格式的字節數據
#             success, img_encoded = cv2.imencode('.jpg', frame)
#             # 如果編碼失敗，返回錯誤響應
#             if not success:
#                 return JsonResponse({"status": "error", "message": "Image encoding failed"}, status=500)
            
#             # 將編碼的圖像數據轉換為字節串
#             data = img_encoded.tobytes()
#             # 添加結束標誌
#             data += b'EOF'
#             print(f"Size of encoded image data: {len(data)} bytes")
     
            
#             r1 = socketclient.sock1(data)
#             r2 = socketclient.sock2(data)
#             if r1 is not None:
#                 d1 = object_continue.con(r1)
#             else:
#                 d1 = " "
#             if r2 is not None:
#                  d2 = face_continue.facecon(r2)
#             else:
#                 d2 = " "
            

#             result = d1+d2

#             return JsonResponse({"status": "success","message":result},status=200)

#         except Exception as e:
#             # 處理過程中可能出現的錯誤，返回錯誤響應
#             return JsonResponse({"status": "error", "message": str(e)}, status=500)
#     else:
#         # 如果請求方法不是 POST 或沒有文件，返回錯誤響應
#         return JsonResponse({"status": "error", "message": "Invalid request."}, status=400)


# #前端丟入物品辨識模型
# @csrf_exempt
# def object_view(request):
#     # 檢查請求方法是否為 POST，且請求中是否包含文件
#     if request.method == 'POST' and 'file' in request.FILES:
#         # 取得上傳的文件
#         uploaded_file = request.FILES['file']
#         try:
#             # 讀取文件數據並將其轉換為 numpy 陣列
#             img_array = np.frombuffer(uploaded_file.read(), np.uint8)
#             # 使用 OpenCV 解碼 numpy 陣列為圖像
#             frame = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

#             # 如果圖像解碼失敗，返回錯誤響應
#             if frame is None:
#                 return JsonResponse({"status": "error", "message": "Image decoding failed."}, status=500)
            
#              # 將圖像保存到本地檔案系統
#             cv2.imwrite('/home/tkuim-sd/image/image.jpg', frame)
#             # 將圖像編碼為 JPEG 格式的字節數據
#             success, img_encoded = cv2.imencode('.jpg', frame)
#             # 如果編碼失敗，返回錯誤響應
#             if not success:
#                 return JsonResponse({"status": "error", "message": "Image encoding failed"}, status=500)
            
#             # 將編碼的圖像數據轉換為字節串
#             data = img_encoded.tobytes()
#             # 添加結束標誌
#             data += b'EOF'
#             print(f"Size of encoded image data: {len(data)} bytes")
#             # 在每次處理之前檢查中斷信號
#             if break_signal.is_set():
#                 return JsonResponse({"status": "error", "message": "Process interrupted by gemini_view"}, status=400)
#             socketclient.sock1(data)
#             socketclient.sock2(data)
#             socketclient.sock3(data)
    
           
#             return JsonResponse({"status": "success"})

#         except Exception as e:
#             # 處理過程中可能出現的錯誤，返回錯誤響應
#             return JsonResponse({"status": "error", "message": str(e)}, status=500)
#     else:
#         # 如果請求方法不是 POST 或沒有文件，返回錯誤響應
#         return JsonResponse({"status": "error", "message": "Invalid request."}, status=400)

                return JsonResponse({"status": "error", "message": "Image decoding failed."}, status=500)
            
            cv2.imwrite('/home/tkuim-sd/image/image.jpg', frame)
            success, img_encoded = cv2.imencode('.jpg', frame)
            if not success:
                return JsonResponse({"status": "error", "message": "Image encoding failed"}, status=500)
            
            data = img_encoded.tobytes()
            data += b'EOF'
            print(f"Size of encoded image data: {len(data)} bytes")
            
            if break_signal.is_set():
                return JsonResponse({"status": "error", "message": "Process interrupted by gemini_view"}, status=400)

            # 使用執行緒並行處理三個模型
            thread1 = threading.Thread(target=send_to_model_1, args=(data,))
            thread2 = threading.Thread(target=send_to_model_2, args=(data,))
            thread3 = threading.Thread(target=send_to_model_3, args=(data,))

            # 啟動所有執行緒
            thread1.start()
            thread2.start()
            thread3.start()

            # 等待所有執行緒完成
            thread1.join()
            thread2.join()
            thread3.join()

            return JsonResponse({"status": "success"})

        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=500)
    else:
        return JsonResponse({"status": "error", "message": "Invalid request."}, status=400)
    
#前端丟入語音模型
@csrf_exempt
def gemini_view(request):
    if request.method != 'POST':
        return JsonResponse({"error": "只接受 POST 请求"})
    # 觸發中斷信號
    break_signal.set()

    # 重置中斷信號，為下一次使用做好準備
    break_signal.clear()
    # 嘗試解析 JSON 數據
    d = json.loads(request.body)
    data = d.get('T')
    # 處理數據的邏輯...
    q = question_input.Objection().ask(data)
    

    return JsonResponse({'status': 'success','message':q},safe=False)


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

        # 將圖像保存到本地檔案系統
        cv2.imwrite('/home/tkuim-sd/image/imagehelp.jpg', frame)
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
                file.write(json.dumps(encoded_str))  # 覆蓋寫入新內容
    
            # 重定向到目标视图
        return redirect('unity_view')
     # 如果不是 POST 請求或沒有文件，返回一個錯誤響應
    return JsonResponse({"status": "error", "message": "Invalid request. No file uploaded."}, status=400)   
            
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
def get_unity1(request):
    if request.method == 'GET':
        with open('get_unity.txt', 'r', encoding='utf-8') as file:
            content1 = file.read()

        r1 = json.loads(content1)

        with open('get_unity.txt', 'w', encoding='utf-8') as file:
            file.write(" ")

        # 处理参数
        response_data = {'player':r1}
        return JsonResponse(response_data)
    
@csrf_exempt
def get_unity2(request):
    if request.method == 'GET':
        with open('unity.txt', 'r', encoding='utf-8') as file:
            content2 = file.read()
        r2 = json.loads(content2)

        # 处理参数
        response_data = {'position':r2}
        return JsonResponse(response_data)



# def continue_view(request):
#     # 檢查請求方法是否為 POST，且請求中是否包含文件
#     if request.method == 'POST' and 'file' in request.FILES:
#         # 取得上傳的文件
#         uploaded_file = request.FILES['file']
#         try:
#             # 讀取文件數據並將其轉換為 numpy 陣列
#             img_array = np.frombuffer(uploaded_file.read(), np.uint8)
#             # 使用 OpenCV 解碼 numpy 陣列為圖像
#             frame = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

#             # 如果圖像解碼失敗，返回錯誤響應
#             if frame is None:
#                 return JsonResponse({"status": "error", "message": "Image decoding failed."}, status=500)

#             # 將圖像編碼為 JPEG 格式的字節數據
#             success, img_encoded = cv2.imencode('.jpg', frame)
#             # 如果編碼失敗，返回錯誤響應
#             if not success:
#                 return JsonResponse({"status": "error", "message": "Image encoding failed"}, status=500)
            
#             # 將編碼的圖像數據轉換為字節串
#             data = img_encoded.tobytes()
#             # 添加結束標誌
#             data += b'EOF'
#             print(f"Size of encoded image data: {len(data)} bytes")
     
            
#             r1 = socketclient.sock1(data)
#             r2 = socketclient.sock2(data)
#             if r1 is not None:
#                 d1 = object_continue.con(r1)
#             else:
#                 d1 = " "
#             if r2 is not None:
#                  d2 = face_continue.facecon(r2)
#             else:
#                 d2 = " "
            

#             result = d1+d2

#             return JsonResponse({"status": "success","message":result},status=200)

#         except Exception as e:
#             # 處理過程中可能出現的錯誤，返回錯誤響應
#             return JsonResponse({"status": "error", "message": str(e)}, status=500)
#     else:
#         # 如果請求方法不是 POST 或沒有文件，返回錯誤響應
#         return JsonResponse({"status": "error", "message": "Invalid request."}, status=400)


# #前端丟入物品辨識模型
# @csrf_exempt
# def object_view(request):
#     # 檢查請求方法是否為 POST，且請求中是否包含文件
#     if request.method == 'POST' and 'file' in request.FILES:
#         # 取得上傳的文件
#         uploaded_file = request.FILES['file']
#         try:
#             # 讀取文件數據並將其轉換為 numpy 陣列
#             img_array = np.frombuffer(uploaded_file.read(), np.uint8)
#             # 使用 OpenCV 解碼 numpy 陣列為圖像
#             frame = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

#             # 如果圖像解碼失敗，返回錯誤響應
#             if frame is None:
#                 return JsonResponse({"status": "error", "message": "Image decoding failed."}, status=500)
            
#              # 將圖像保存到本地檔案系統
#             cv2.imwrite('/home/tkuim-sd/image/image.jpg', frame)
#             # 將圖像編碼為 JPEG 格式的字節數據
#             success, img_encoded = cv2.imencode('.jpg', frame)
#             # 如果編碼失敗，返回錯誤響應
#             if not success:
#                 return JsonResponse({"status": "error", "message": "Image encoding failed"}, status=500)
            
#             # 將編碼的圖像數據轉換為字節串
#             data = img_encoded.tobytes()
#             # 添加結束標誌
#             data += b'EOF'
#             print(f"Size of encoded image data: {len(data)} bytes")
#             # 在每次處理之前檢查中斷信號
#             if break_signal.is_set():
#                 return JsonResponse({"status": "error", "message": "Process interrupted by gemini_view"}, status=400)
#             socketclient.sock1(data)
#             socketclient.sock2(data)
#             socketclient.sock3(data)
    
           
#             return JsonResponse({"status": "success"})

#         except Exception as e:
#             # 處理過程中可能出現的錯誤，返回錯誤響應
#             return JsonResponse({"status": "error", "message": str(e)}, status=500)
#     else:
#         # 如果請求方法不是 POST 或沒有文件，返回錯誤響應
#         return JsonResponse({"status": "error", "message": "Invalid request."}, status=400)



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


