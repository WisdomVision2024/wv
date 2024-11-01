import face_recognition as fr  # 用於人臉識別
import numpy as np  # 用於處理所有列表/陣列
import cv2  # 用於處理影像操作
import os  # 用於處理資料夾、路徑、圖片/檔案名稱等
import json  # 用於處理 JSON 格式
import socket
import select
import app.question_input as question_input
import app.face_continue as face_continue
import logging
import concurrent.futures
# 設定 logging 格式
logging.basicConfig(format='%(asctime)s - %(message)s - [%(funcName)s:%(lineno)d]', level=logging.DEBUG)

# 已知人臉的資料夾路徑
faces_path = f'/home/tkuim-sd/wv/media/image'

import face_recognition as fr
import numpy as np
import cv2
import os
import json


class FaceRecognition:
    def __init__(self, faces_path='/home/tkuim-sd/wv/media/image'):
        self.faces_path = faces_path
        self.face_encodings, self.face_names = self.load_cached_encodings()

    def get_face_encodings(self):
        """
        獲取已知人臉的名稱和編碼
        :return: 人臉編碼列表和人臉名稱列表
        """
        face_names = os.listdir(self.faces_path)
        face_encodings = []

        for i, name in enumerate(face_names):
            face = fr.load_image_file(os.path.join(self.faces_path, name))
            encodings = fr.face_encodings(face)
            if encodings:  # 確保人臉編碼存在
                face_encodings.append(encodings[0])
                face_names[i] = name.split(".")[0]  # 去除圖片副檔名

        return face_encodings, face_names

    def load_cached_encodings(self):
        """
        加載已知人臉編碼，如果有緩存則從緩存載入
        :return: 人臉編碼和名稱列表
        """
        if os.path.exists("face_encodings.npy") and os.path.exists("face_names.npy"):
            face_encodings = np.load("face_encodings.npy", allow_pickle=True)
            face_names = np.load("face_names.npy", allow_pickle=True)
        else:
            face_encodings, face_names = self.get_face_encodings()
            np.save("face_encodings.npy", face_encodings)
            np.save("face_names.npy", face_names)
        return face_encodings, face_names

    def recognize_faces(self, image):
        """
        對指定圖片進行人臉識別並返回結果
        :param image: 要識別的圖片
        :return: 識別結果（包含名字和信心度）以及標註人臉的圖片
        """
        face_locations = fr.face_locations(image)
        unknown_encodings = fr.face_encodings(image, face_locations)

        results = []  # 存儲識別結果的列表

        for face_encoding, face_location in zip(unknown_encodings, face_locations):
            face_distances = fr.face_distance(self.face_encodings, face_encoding)
            best_match_index = np.argmin(face_distances)
            best_distance = face_distances[best_match_index]
            confidence = max(0, 1 - best_distance)

            if confidence > 0.6:  # 設定匹配閾值
                name = self.face_names[best_match_index]
                top, right, bottom, left = face_location

                # 在人臉周圍畫矩形
                cv2.rectangle(image, (left, top), (right, bottom), (0, 0, 255), 2)

                # 顯示名字和信心度
                font = cv2.FONT_HERSHEY_DUPLEX
                cv2.putText(image, f"{name} ({confidence:.2f})", (left, bottom + 20), font, 0.8, (255, 255, 255), 1)

                results.append({
                    "name": name,
                    "confidence": confidence
                })

        bgr_image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        return results, bgr_image

    def get_results_json(self, image):
        """
        獲取識別結果的 JSON 格式
        :param image: 要識別的圖片
        :return: JSON 格式的識別結果
        """
        results, _ = self.recognize_faces(image)
        return json.dumps(results, indent=4)

    def start_socket_server(self, host='localhost', port=5555):
        # 創建 TCP 套接字
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((host, port))
        server_socket.setblocking(False)
        server_socket.listen()
        print(f'Socket server started at {host}:{port}')

        sockets_list = [server_socket]
        clients = {}

        while True:
            read_sockets, _, exception_sockets = select.select(sockets_list, [], sockets_list)

            for notified_socket in read_sockets:
                if notified_socket == server_socket:
                    client_socket, addr = server_socket.accept()
                    client_socket.setblocking(False)
                    sockets_list.append(client_socket)
                    clients[client_socket] = b""
                    print(f'Connected by {addr}')
                else:
                    try:
                        packet = notified_socket.recv(100000)
                        if not packet:
                            sockets_list.remove(notified_socket)
                            del clients[notified_socket]
                            notified_socket.close()
                            continue

                        clients[notified_socket] += packet
                        print(f"Size of encoded image data: {len(clients[notified_socket])} bytes")

                        if b'EOF' in clients[notified_socket]:
                            data = clients[notified_socket].split(b'EOF')[0]
                            img_array = np.frombuffer(data, np.uint8)
                            frame = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

                            if frame is not None:
                                results, annotated_image = self.recognize_faces(frame)
                                # # 顯示結果圖片
                                # cv2.imshow("Image", annotated_image)
                                # cv2.waitKey(0)
                                # cv2.destroyAllWindows()

                                json_result = self.get_results_json(frame)
                                logging.debug(json_result)
                                self.send_to_speech_model(json_result)


                                notified_socket.sendall(json_result.encode('utf-8'))

                            sockets_list.remove(notified_socket)
                            del clients[notified_socket]
                            notified_socket.close()

                    except Exception as e:
                        print(f"Error: {e}")
                        sockets_list.remove(notified_socket)
                        del clients[notified_socket]
                        notified_socket.close()

            for notified_socket in exception_sockets:
                sockets_list.remove(notified_socket)
                del clients[notified_socket]
                notified_socket.close()

    def send_to_speech_model(self, data):
        # 將處理結果發送到語音模型
        dec = question_input.Objection()
        dec.img_face(data)
    


if __name__ == '__main__':
    detector = FaceRecognition()
    detector.start_socket_server()





# class ObjectDetection:
#     # 函數：獲取人臉名稱和人臉編碼
#     @staticmethod
#     def get_face_encodings():
#         face_names = os.listdir(faces_path)
#         face_encodings = []

#         # 使用迴圈檢索所有人臉編碼並存儲到列表中
#         for i, name in enumerate(face_names):
#             face = fr.load_image_file(f"{faces_path}/{name}")
#             face_encodings.append(fr.face_encodings(face)[0])

#             face_names[i] = name.split(".")[0]  # 去除 ".jpg" 或其他圖片副檔名

#         return face_encodings, face_names
    
#     def face(self, frame):
#         # 獲取人臉編碼並將其存儲到 face_encodings 變數中，還有名字
#         face_encodings, face_names = ObjectDetection.get_face_encodings()

#         # 獲取人臉位置座標和未知人臉編碼
#         face_locations = fr.face_locations(frame)
#         unknown_encodings = fr.face_encodings(frame, face_locations)

#         # 用於存儲 JSON 結果的列表
#         results = []

#         # 遍歷每個編碼及人臉位置
#         for face_encoding, face_location in zip(unknown_encodings, face_locations):
#             # 計算與已知人臉編碼的距離
#             face_distances = fr.face_distance(face_encodings, face_encoding)

#             # 找到最小距離的索引（最接近的已知人臉編碼）
#             best_match_index = np.argmin(face_distances)
#             best_distance = face_distances[best_match_index]

#             # 計算信心度（信心度可以設定為 1 - 距離）
#             confidence = max(0, 1 - best_distance)  # 保證信心度不為負值

#             # 設定匹配閾值（例如 0.6）
#             if confidence > 0.6:  # 可根據需要調整閾值
#                 name = face_names[best_match_index]

#                 # 設定人臉位置的座標
#                 top, right, bottom, left = face_location

#                 # 在人臉周圍畫矩形
#                 cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

#                 # 設置字體並顯示名字文字
#                 font = cv2.FONT_HERSHEY_DUPLEX
#                 cv2.putText(frame, f"{name} ({confidence:.2f})", (left, bottom + 20), font, 0.8, (255, 255, 255), 1)

#                 # 將結果加入 JSON 列表
#                 results.append({
#                     "name": name,
#                     "confidence": confidence,
#                 })

#         # 將圖片從 RGB 轉換回 BGR，因為 OpenCV 使用 BGR
#         bgr_image = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)



#         # 等待直到使用者按下任意鍵關閉視窗
#         cv2.waitKey(0)
#         cv2.destroyAllWindows()

#         # 輸出 JSON 格式的結果
#         return json.dumps(results, indent=4)

#     def start_socket_server(self, host='localhost', port=5555):
#         # 創建 TCP 套接字
#         server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#         # 綁定主機和端口
#         server_socket.bind((host, port))
#         # 設置套接字為非阻塞模式
#         server_socket.setblocking(False)
#         # 開始監聽連接
#         server_socket.listen()
#         print(f'Socket server started at {host}:{port}')

#         # 用來追蹤所有活躍的套接字（包括伺服器套接字）
#         sockets_list = [server_socket]
#         # 用來儲存每個客戶端的數據
#         clients = {}

#         while True:
#             # 使用 select 函數來監控套接字
#             # read_sockets: 可讀的套接字
#             # exception_sockets: 異常的套接字
#             read_sockets, _, exception_sockets = select.select(sockets_list, [], sockets_list)

#             for notified_socket in read_sockets:
#                 if notified_socket == server_socket:
#                     # 如果是伺服器套接字，接受新的客戶端連接
#                     client_socket, addr = server_socket.accept()
#                     # 設置客戶端套接字為非阻塞模式
#                     client_socket.setblocking(False)
#                     # 將客戶端套接字添加到監控列表
#                     sockets_list.append(client_socket)
#                     # 初始化客戶端數據儲存
#                     clients[client_socket] = b""
#                     print(f'Connected by {addr}')
#                 else:
#                     try:
#                         # 接收來自客戶端的數據
#                         packet = notified_socket.recv(100000)
                        
#                         if not packet:
#                             # 如果未收到數據（客戶端關閉連接），處理該客戶端
#                             sockets_list.remove(notified_socket)
#                             del clients[notified_socket]
#                             notified_socket.close()
#                             continue

#                         # 將接收到的數據添加到對應的客戶端數據中
#                         clients[notified_socket] += packet
#                         print(f"Size of encoded image data: {len(clients[notified_socket])} bytes")
                        
#                         # 當接收到完整的數據後進行處理
#                         if b'EOF' in clients[notified_socket]:
#                             # 提取數據部分（排除 EOF 標記）
#                             data = clients[notified_socket].split(b'EOF')[0]
#                             # 將數據轉換為 numpy 陣列
#                             img_array = np.frombuffer(data, np.uint8)
#                             # 解碼為圖像
#                             frame = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

#                             if frame is not None:
#                                 # 使用 ObjectDetection 類別進行預測
#                                 face_results = ObjectDetection().face(frame)
#                                 # 將結果發送到語音模型
#                                 self.send_to_speech_model(face_results)

                                
#                                 logging.debug(face_results)
#                                 # F_c = face_continue.facecon(face_results)
                                
#                                 notified_socket.sendall(face_results.encode('utf-8'))

#                             # 清除已處理的客戶端數據
#                             sockets_list.remove(notified_socket)
#                             del clients[notified_socket]
#                             notified_socket.close()

#                     except Exception as e:
#                         # 處理接收過程中的例外
#                         print(f"Error: {e}")
#                         # 清除有錯誤的客戶端
#                         sockets_list.remove(notified_socket)
#                         del clients[notified_socket]
#                         notified_socket.close()

#             for notified_socket in exception_sockets:
#                 # 處理異常套接字（可能是錯誤或問題的連接）
#                 sockets_list.remove(notified_socket)
#                 del clients[notified_socket]
#                 notified_socket.close()

#     def send_to_speech_model(self, data):
#         # 將處理結果發送到語音模型
#         dec = question_input.Objection()
#         dec.img_face(data)
      


# if __name__ == '__main__':
#     detector = ObjectDetection()
#     detector.start_socket_server()