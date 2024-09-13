import cv2
from ultralytics import YOLO
import torch
import json
import select
import socket
import numpy as np
import app.question_input as question_input
import logging

# 設定 logging 格式
logging.basicConfig(format='%(asctime)s - %(message)s - [%(funcName)s:%(lineno)d]', level=logging.DEBUG)
class ObjectDetection:

    # # 定義座標字典
    # coordinates = {
    #     'A': (46.5, 0), 'B': (46.5, 70), 'C': (46.5, 140), 'D': (46.5, 210), 'E': (46.5, 280),
    #     'F': (46.5, 350), 'L': (46.5, 400), 'Q': (116.5, 400), 'P': (186.5, 400), 'K': (256.5, 400),
    #     'U': (326.5, 400), 'V': (396.5, 400), 'W': (466.5, 400), 'X': (536.5, 400), 'Y': (606.5, 400),
    #     'Z': (668.5, 400), 'e': (668.5, 350), 'h': (668.5, 280), 'm': (668.5, 210), 'n': (668.5, 140),
    #     'g': (676.5, 55), 't': (606.5, 55), 'y': (536.5, 55), 'lungu': (466.5, 55), 'duomianti': (396.5, 55),
    #     'r': (326.5, 55), 'yuanzhu': (256.5, 55), 'yuanzhui': (186.5, 55), '4': (116.5, 55)
    # }
    
    # 定義座標字典
    coordinates = {
        'A':(403.0,1.81,63.0),
        'B':(418.0,1.81,63.0),
        'C':(433.0,1.81,63.0),
        'D':(448.0, 1.81, 63.0), 
        'E':(463.0, 1.81, 63.0),
        'F':(478.0, 1.81, 63.0),
        'L': (493.0, 1.81, 63.0), 
        'Q': (508.0, 1.81, 63.0) , 
        'P': (523.0, 1.81, 63.0) , 
        'K': (538.0, 1.81, 63.0) ,
        'U': (538.0, 1.81, 48.2) , 
        'V': (538.0, 1.81, 33.4), 
        'W': (538.0, 1.81, 18.6), 
        'X': (538.0, 1.81, 3.8) ,
        'Y': (538.0, 1.81, -11.0),
        'Z': (523.0, 1.81, -11.0), 
        'e': (508.0, 1.81, -11.0), 
        'h': (493.0, 1.81, -11.0), 
        'm': (478.0, 1.81, -11.0), 
        'n': (463.0, 1.81, -11.0),
        'g': (448.0, 1.81, -11.0), 
        't': (433.0, 1.81, -11.0), 
        'y': (418.0, 1.81, -11.0), 
        'lungu': (403.0, 1.81, -11.0), 
        'duomianti': (403.0, 1.81, 3.8),
        'r': (403.0, 1.81, 18.6), 
        'yuanzhu': (403.0, 1.81, 33.4), 
        'yuanzhui': (403.0, 1.81, 48.2), 
        '4': (403.0, 1.81, 63.0)
    }




    def __init__(self):
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        print("Using Device: ", self.device)
        self.model = self.load_model()
        self.CLASS_NAMES_DICT = self.model.model.names

    def load_model(self):
        model = YOLO("/home/tkuim-sd/wv/app/position/train11/weights/best.pt")  # load a pretrained YOLOv8 model
        model.fuse()
        model.to(self.device)
        return model

    def position(self, frame):
        # 使用模型進行推論
        results = self.model(frame)

        # 確保 results 是有效的對象
        if not results:
            return "Error: No results returned from the YOLO model."

        # 獲取標籤名稱的映射
        names = self.model.names

        re = []
        # 從結果中獲取標籤和座標
        for result in results:
            for box in result.boxes:
                if box.xyxy is None or box.cls is None:
                    continue  # 跳過無效的檢測結果

                x1, y1, x2, y2 = box.xyxy[0].tolist()  # 取得邊界框座標
                label_id = int(box.cls[0])  # 取得標籤ID
                label_name = names.get(label_id, "Unknown")  # 取得標籤名稱
                coordinate = self.coordinates.get(label_name)  # 根據標籤名稱取得座標

                # 確認座標是否存在
                if coordinate is None:
                    print(f"Warning: No coordinates found for label '{label_name}'")
                    continue  # 跳過沒有座標的標籤
                 
                # 將結果加入 JSON 列表
                re.append({
                    "x": coordinate[0],
                    "y": coordinate[1],
                    "z": coordinate[2],
                })
        logging.debug(json.dumps(re, indent=4))
                   # 輸出 JSON 格式的結果
        return json.dumps(re, indent=4)
    
    def start_socket_server(self, host='localhost', port=6666):
        # 創建 TCP 套接字
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((host, port))
        server_socket.setblocking(False)
        server_socket.listen()
        print(f'Socket server started at {host}:{port}')

        sockets_list = [server_socket]
        clients = {}

        while True:
            # 使用 select 函數來監控套接字
            read_sockets, _, exception_sockets = select.select(sockets_list, [], sockets_list)
            
            for notified_socket in read_sockets:
                if notified_socket == server_socket:
                    # 接受新的客戶端連接
                    client_socket, addr = server_socket.accept()
                    client_socket.setblocking(False)
                    sockets_list.append(client_socket)
                    clients[client_socket] = b""
                    print(f'Connected by {addr}')
                else:
                    try:
                        # 接收來自客戶端的數據
                        packet = notified_socket.recv(100000)
                        
                        if not packet:
                            # 客戶端關閉連接
                            sockets_list.remove(notified_socket)
                            del clients[notified_socket]
                            notified_socket.close()
                            continue

                        # 將接收到的數據添加到對應的客戶端數據中
                        clients[notified_socket] += packet
                        print(f"Size of encoded image data: {len(clients[notified_socket])} bytes")

                        # 當接收到完整的數據後進行處理
                        if b'EOF' in clients[notified_socket]:
                            data = clients[notified_socket].split(b'EOF')[0]
                            img_array = np.frombuffer(data, np.uint8)
                            frame = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
                            if frame is not None:
                                # 使用 ObjectDetection 類別進行預測
                                objectface_results = self.position(frame)
                                # 將結果發送到語音模型
                  
                                self.send_to_speech_model(objectface_results)

                                # 將語音模型結果回傳給客戶端
                                notified_socket.sendall(objectface_results.encode('utf-8'))
                            # 清除已處理的客戶端數據
                            sockets_list.remove(notified_socket)
                            del clients[notified_socket]
                            notified_socket.close()
                    except (socket.error, cv2.error) as e:
                        print(f"Socket or OpenCV error: {e}")
                        if notified_socket in sockets_list:
                            sockets_list.remove(notified_socket)
                        if notified_socket in clients:
                            del clients[notified_socket]
                        notified_socket.close()

            for notified_socket in exception_sockets:
                # 處理異常套接字
                if notified_socket in sockets_list:
                    sockets_list.remove(notified_socket)
                if notified_socket in clients:
                    del clients[notified_socket]
                notified_socket.close()

    # def send_to_unity(self, data):
    #     return data
    
    def send_to_speech_model(self, data):
        # 將處理結果發送到語音模型
        dec = question_input.Objection()
        dec.img_point(data)
      
if __name__ == '__main__':
    detector = ObjectDetection()
    detector.start_socket_server()