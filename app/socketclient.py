import numpy as np
import cv2
from time import time,sleep
from ultralytics import YOLO
import os
from collections import Counter
import socket
import select
import test
import struct
import logging
from datetime import datetime

# 獲取當前時間
now = datetime.now()

# 設定 logging 格式
logging.basicConfig(format='%(asctime)s - %(message)s - [%(funcName)s:%(lineno)d]', level=logging.DEBUG)

     
# 創建 Socket 連接到 YOLO 模型服務器

import struct
import os



def sock1(data):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.setblocking(False)  # 設置為非阻塞模式
    try:
        # 嘗試連接到服務器，使用 connect_ex 以避免阻塞
        client_socket.connect_ex(('localhost', 8002))
    except BlockingIOError:
        # 忽略非阻塞模式下的異常
        pass
    # 使用 select 來等待 socket 可寫，以確認連接完成
    _, writable, _ = select.select([], [client_socket], [])
    # 如果 socket 不可寫，則拋出異常
    if not writable:
        raise Exception("Unable to connect to the server.")

   # 發送圖像數據
    while data:
       _, writable, _ = select.select([], [client_socket], [])
       # 如果 socket 可寫，發送數據
       if writable:
           sent = client_socket.send(data)
           data = data[sent:]  # 更新剩餘數據

   # 接收來自模型的返回數據
    response = b""
    while True:
       # 使用 select 來等待 socket 可讀
       readable, _, _ = select.select([client_socket], [], [], 5)
       if readable:
           # 接收數據包
           packet = client_socket.recv(100000)
           # 如果未接收到數據，則退出
           if not packet:
               break
           # 將數據包添加到響應中
           response += packet
           # 如果響應中包含 EOF，則退出
           if b'EOF' in response:
               break
    
    # 關閉 socket 連接
    client_socket.close()

    # 解析返回的 JSON 結果
    result_data = response.decode('utf-8')
    return result_data

def sock2(data):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.setblocking(False)  # 設置為非阻塞模式
    try:
        # 嘗試連接到服務器，使用 connect_ex 以避免阻塞
        client_socket.connect_ex(('localhost', 4445))
    except BlockingIOError:
        # 忽略非阻塞模式下的異常
        pass
    # 使用 select 來等待 socket 可寫，以確認連接完成
    _, writable, _ = select.select([], [client_socket], [])
    # 如果 socket 不可寫，則拋出異常
    if not writable:
        raise Exception("Unable to connect to the server.")

   # 發送圖像數據
    while data:
       _, writable, _ = select.select([], [client_socket], [])
       # 如果 socket 可寫，發送數據
       if writable:
           sent = client_socket.send(data)
           data = data[sent:]  # 更新剩餘數據

   # 接收來自模型的返回數據
    response = b""
    while True:
       # 使用 select 來等待 socket 可讀
       readable, _, _ = select.select([client_socket], [], [], 5)
       if readable:
           # 接收數據包
           packet = client_socket.recv(100000)
           # 如果未接收到數據，則退出
           if not packet:
               break
           # 將數據包添加到響應中
           response += packet
           # 如果響應中包含 EOF，則退出
           if b'EOF' in response:
               break

    # 關閉 socket 連接
    client_socket.close()

    # 解析返回的 JSON 結果
    result_data = response.decode('utf-8')
    return result_data


def sock3(data):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.setblocking(False)  # 設置為非阻塞模式
    try:
        # 嘗試連接到服務器，使用 connect_ex 以避免阻塞
        client_socket.connect_ex(('localhost', 8003))
    except BlockingIOError:
        # 忽略非阻塞模式下的異常
        pass
    # 使用 select 來等待 socket 可寫，以確認連接完成
    _, writable, _ = select.select([], [client_socket], [])
    # 如果 socket 不可寫，則拋出異常
    if not writable:
        raise Exception("Unable to connect to the server.")

   # 發送圖像數據
    while data:
       _, writable, _ = select.select([], [client_socket], [])
       # 如果 socket 可寫，發送數據
       if writable:
           sent = client_socket.send(data)
           data = data[sent:]  # 更新剩餘數據

   # 接收來自模型的返回數據
    response = b""
    while True:
       # 使用 select 來等待 socket 可讀
       readable, _, _ = select.select([client_socket], [], [], 5)
       if readable:
           # 接收數據包
           packet = client_socket.recv(100000)
           # 如果未接收到數據，則退出
           if not packet:
               break
           # 將數據包添加到響應中
           response += packet
           # 如果響應中包含 EOF，則退出
           if b'EOF' in response:
               break

    # 關閉 socket 連接
    client_socket.close()

  
     # 解析返回的 JSON 結果
    result_data = response.decode('utf-8')
    return response


    