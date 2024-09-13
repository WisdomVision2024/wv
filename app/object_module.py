import torch
import numpy as np
import cv2
from time import time,sleep
from ultralytics import YOLO
import os
from collections import Counter
import socket
import select
import json  # 用於處理 JSON 格式
import test
import app.object_continue as object_continue
import app.question_input as question_input
import logging


# 設定 logging 格式
logging.basicConfig(format='%(asctime)s - %(message)s - [%(funcName)s:%(lineno)d]', level=logging.DEBUG)

# print("abc")
# result = test.ongoing.Objection().con()
# print(result)
# print("abc end")

class ObjectDetection:
    
    def __init__(self):
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        print("Using Device: ", self.device)
        self.model = self.load_model()
        self.CLASS_NAMES_DICT = self.model.model.names
        self.a = ""

    def load_model(self):
        model = YOLO("/home/tkuim-sd/wv/app/Total.pt")  # load a pretrained YOLOv8 model
        model.fuse()
        model.to(self.device)
        return model

    def predict(self, frame):
        results = self.model(frame)
        re = []
        for result in results:
            boxes = result.boxes.cpu().numpy()
            for box, conf, cls in zip(boxes.xyxy,boxes.conf,boxes.cls):
                class_id = int(cls)
                class_name = result.names[class_id] if result.names else f"Class {class_id}"
                re.append({
                    "name":result.names[int(cls)],
                    "class":class_id,
                    "confidence" : conf.tolist(),
                        "box":{ "x1": float(box[0]),  # 將 `float32` 轉換為 `float`
                                "y1": float(box[1]),
                                "x2": float(box[2]),
                                "y2": float(box[3])},
                    
                })
        return json.dumps(re, indent=4)


    def plot_bboxes(self, results, frame):
        xyxys = []
        confidences = []
        class_ids = []
        class_count = []

        # Extract detections for person class
        for result in results:
            boxes = result.boxes.cpu().numpy()
            xyxys.append(boxes.xyxy)
            confidences.append(boxes.conf)
            class_ids.append(boxes.cls)

        # Use YOLOv8's built-in plotting function to draw bounding boxes on the image
        frame_with_bboxes = results[0].plot()

        return frame_with_bboxes, xyxys, confidences, class_ids

    def process_image(self, image_path):
        frame = cv2.imread(image_path)

        if frame is None:
            print(f"Error reading image: {image_path}")
            return

        start_time = time()
        results = self.predict(frame)
        frame_with_bboxes, xyxys, confidences, class_ids = self.plot_bboxes(results, frame)

        # Print results
        print(f"Results for {os.path.basename(image_path)}:")
        image_result = results[0].verbose()     # 顯示圖片中辨識出的物品種類和數量
        print(image_result)

        json_result = results[0].tojson()       # 辨識結果json格式
        print(json_result)

        end_time = time()
        fps = 1 / np.round(end_time - start_time, 2)

        # Display the processed frame
        cv2.imshow(f'YOLOv8 Detection - {os.path.basename(image_path)}', frame_with_bboxes)
        cv2.waitKey(3000)
        cv2.destroyAllWindows()

    def start_socket_server(self, host='localhost', port=4444):
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
                                object_results = self.predict(frame)
                                # 將結果發送到語音模型
                                self.send_to_speech_model(object_results)

                                #結果送至object_continue
                                # O_c = object_continue.con(object_results)
                                logging.debug(object_results)
                                # 將語音模型結果回傳給客戶端
                                notified_socket.sendall(object_results.encode('utf-8'))

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

    def send_to_speech_model(self, data):
        # 將處理結果發送到語音模型
        #print(f"Data received: {data}")  # 調試用輸出  
        # 創建一個列表來存儲每張圖片的預測結果
        dec = question_input.Objection()
        dec.img_object(data)
    
     
       
    

if __name__ == '__main__':
    detector = ObjectDetection()
    detector.start_socket_server()


    