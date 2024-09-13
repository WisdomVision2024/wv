from app import object,face,point
#串接GEMINI
import google.generativeai as genai
import os
import logging
import json
import time
# 設定 logging 格式
logging.basicConfig(format='%(asctime)s - %(message)s - [%(funcName)s:%(lineno)d]', level=logging.DEBUG)

api_key = 'AIzaSyBCcg0skdWwwG-hBucIvDCLHY9FFtzw9-0'
genai.configure(api_key = api_key)
model = genai.GenerativeModel('gemini-pro')

class Objection:
    def __init__(self):
        self.question = ""  
        self.distribution = ""
     

    def ask(self,question):
        with open('img_point.txt', 'w') as file:
            file.write(" ")  # 清空檔案
        with open('img_object.txt', 'w') as file:
            file.write(" ")  # 清空檔案
        with open('img_face.txt', 'w') as file:
            file.write(" ")  # 清空檔案

        self.question = question
        logging.debug(self.question)
        a='1.標點類問題:使用者身下共有29個標點，此類問題是與位置資訊相關，所有有關環境資訊的問題，皆屬於這類問題，只要是使用者位置資訊相關的問題，皆為此類問題，通常問題中的「我」即代表使用者。Ex:(1)問題：我現在在哪?思考過程：問題中提到了使用者的位置資訊，因此屬於標點類問題。？(2)我這附近有甚麼東西(3)我在哪?2.物品類問題:此類問題提到使用者前方視野中有甚麼物品，主要為前方視野的物品相關的問題，屬於此類問題。此類問題的詢問方向將會聚焦在使用者前方，因此如果問題中包含「附近」這種指向全方向的，超出前方視野範圍的，將不屬於此類問題，假設問題為:我的附近有甚麼。由於附近指的是使用者周圍，超過了前方的範圍，因此答案應該為：1. 標點類問題，若你回答2.物品類問題，則屬於錯誤回答。請記住，人物不屬於物品，如果問題中出現人物相關的關鍵字，將絕對不屬於此類問題。Ex:(1)我的前方有甚麼？(2)我的前方有水壺嗎？3.人物類問題: 所有提到了使用者之外的人物的問題都屬於此類問題此為最優先級的判斷，只要問題中包含「人」，即屬於這類問題。這是你剛剛的錯誤回答，問題為:我的前方有誰。你的回答為:2. 物品類問題。由於問題中提到了「誰」這個字，因此代表這個問題是屬於人物相關的問題，即便問題中養提到前方，只要問題與人物相關，就是屬於人物類問題，因此正確答案應該為:3.人物類問題。問題中提到其他人物必須屬於這一類，關鍵字如「誰」，或人名例如:Paney、Irene、Huang等，或周圍有多少人等涉及人的一切問題，都屬於此類問題。Ex: (1)人員位置：附近有我認識的人嗎?(2)我的前方有誰(3)前面的人是小華嗎？(4)此為你剛剛的錯誤案例:問題:你知道廁所在哪嗎。你的錯誤回答:3.人物類問題。錯誤原因:通常使用者問題中的「你」若為主詞，都是在指你，geminiAI，並不屬於人物，這個問題主要是在問廁所在哪裡，是跟環境資訊相關的問題，因此最終正確答案應為:1.標點類問題。4.其他類問題:此類問題為上述三類問題以外的問題，與位置資訊無關的問題，即包含在此類問題，可能包括閒聊等日常對話、問候。Ex:(1)今天天氣真好(2)你知道一加一等於多少嗎?(3)你好啊(4)你會製作蛋糕嗎'

        response = model.generate_content("使用者問題:「"+self.question+"」問題結束。請根據問題分類:「"+a+"」判斷問題屬於四種問題的哪一種，請回答問題屬於四種問題的哪一種(回答格式為:1.標點類問題；2.物品類問題；3.人物類問題；4.其他類問題)，請隱藏思考過程直接給我答案，ex:假設問題為:我的前方有甚麼請回答:2.物品類問題")
        #print(response.text)
        #判斷
        keyworda = ["標點類問題"]
        keywordb = ["物品類問題"]
        keywordc = ["人物類問題"]
        keywordd = ["其他類問題"]
        self.distribution= response.text
        logging.debug(self.distribution)

        

        #標點類
        for keyword in keyworda:
            if keyword in self.distribution:
                timeout = 20  # 設定超時時間為 20 秒
                start_time = time.time()


                while True:
                    try:
                        with open('img_point.txt', 'r') as file:
                            content1 = file.read().strip()  # 去除空白字符，避免空行干擾
                            
                        if content1:  # 假設 content 解析成功
                            logging.debug(f"讀取到的資料: {content1}")
                            break  # 解析成功，跳出迴圈
                        
                        if time.time() - start_time > timeout:  # 超時檢查
                            return "等待超時，無法取得足夠的資料"

                        time.sleep(0.1)  # 稍微等待，減少忙碌輪詢
                    except FileNotFoundError:
                        logging.error("文件不存在，等待寫入...")
                        time.sleep(0.1)  # 等待一段時間再嘗試

                # 假設 content 已經解析成功
                try:
                    contents1 = json.loads(content1)  # 嘗試解析 JSON
                except json.JSONDecodeError as e:
                    return f"無法解析 JSON 資料: {e}"

                ans = point.point(self.question, contents1)  # 傳入解析後的 JSON
                return ans
        
        #物品類
        for keyword in keywordb:
            if keyword in self.distribution:
      
                timeout = 20  # 設定超時時間為 20 秒
                start_time = time.time()

                while True:
                    try:
                        with open('img_object.txt', 'r') as file:
                            content2 = file.read().strip()  # 去除空白字符，避免空行干擾
                            
                        if content2:  # 假設 content 解析成功
                            logging.debug(f"讀取到的資料: {content2}")
                            break  # 解析成功，跳出迴圈
                        
                        if time.time() - start_time > timeout:  # 超時檢查
                            return "等待超時，無法取得足夠的資料"

                        time.sleep(0.1)  # 稍微等待，減少忙碌輪詢
                    except FileNotFoundError:
                        logging.error("文件不存在，等待寫入...")
                        time.sleep(0.1)  # 等待一段時間再嘗試

                # 假設 content 已經解析成功
                try:
                    contents2 = json.loads(content2)  # 嘗試解析 JSON
                except json.JSONDecodeError as e:
                    return f"無法解析 JSON 資料: {e}"
                
                #輸入辨識結果
                x=object.object(contents2)
                 
                # response = model.generate_content("現在一共有六種物品，分別是書、水壺、椅子、桌子、筆電、筆，接下來會有五個結果敘述出畫面中六種物品的數量，畫面中沒有提到即代表數量為0，同一種物品在不同結果中可能會有不同數量，請綜合所有結果，以多數為真的邏輯，整合出最終答案，以下中括號中的文字為例題:[結果一:畫面中有1本書、3個水壺、7張椅子、39張桌子、2枝筆，結果二:畫面中有1本書、3個水壺、7張椅子、40張桌子、1枝筆，結果三:畫面中有1本書、3個水壺、7張椅子、40張桌子、1台筆電、2枝筆，結果四:畫面中有2本書、3個水壺、7張椅子、40張桌子、2枝筆，結果五:畫面中有3個水壺、7張椅子、40張桌子、2枝筆]以下中括號部分為思考過程，接下來請完全參考此過程作答[判斷書:三個結果中書數量為1，一個結果中書數量為2，一個結果中書數量為0，因為最多結果顯示書的數量為1，所以最終書的數量為1；判斷水壺:五個結果中水壺數量為3，因為最多結果顯示水壺的數量為3，所以最終水壺的數量為3；判斷椅子:五個結果中椅子數量為7，因為最多結果顯示椅子的數量為3，所以最終椅子的數量為7；判斷桌子:四個結果中桌子數量為40，一個結果中桌子數量為39，因為最多結果顯示桌子的數量為40，所以最終桌子的數量為40；判斷筆電:4個結果中沒有提到筆電，即代表數量為0，一個結果中筆電數量為，因為最多結果顯示筆電的數量為0，所以最終筆電的數量為0，由於數量為0，最後答案不必顯示；判斷筆:四個結果中筆的數量為2，一個結果中筆的數量為1，因為最多結果顯示筆的數量為2，所以最終筆的數量為2；判斷完所有物品即可整合出答案:畫面中有1本書、3個水壺、7張椅子、40張桌子、2枝筆；以下是你之前回答正確的紀錄，這正是我想要的回答:結果一:畫面中有1本書、2枝筆，結果二:畫面中有1本書、1張桌子、1枝筆，結果三:畫面中有1本書、2張桌子、2枝筆，結果四:畫面中有2張桌子、2枝筆，結果五:畫面中有3張桌子、2枝筆**思考流程：****判斷書：*** 三個結果中書數量為1，兩個結果中書數量為0。* 最多結果顯示書的數量為1，故最終書的數量為1。**判斷筆：*** 五個結果中筆的數量為2，故最終筆的數量為2。**判斷桌子：*** 三個結果中桌子數量為2，兩個結果中桌子數量為1，一個結果中桌子數量為3。* 最多結果顯示桌子的數量為2，故最終桌子的數量為2。]。以下為題目，請參考剛剛的思考流程整合結果，再次強調，我需要的是重複次數最多的答案，請幫我隱藏過程，只留下最終答案:"+x)
                response = model.generate_content("現在"+x+"，此為使用者前方的畫面，請根據此回答問題，請回答完整句子，如果畫面中沒有該物品，就請回答沒有，如果為開放式問題，如:我的前方有什麼，請回答使用者前方的畫面中的所有物品。接下來為問題:"+self.question+"。請注意，問題可能會出現同音錯字，例如:我的前方有比嗎。使用者想表達的是:我的前方有筆嗎。")
        
                return(response.text)
        #人物類
        for keyword in keywordc:
            if keyword in self.distribution:
                timeout = 20  # 設定超時時間為 20 秒
                start_time = time.time()

                while True:
                    try:
                        with open('img_face.txt', 'r') as file:
                            content3 = file.read().strip()  # 去除空白字符，避免空行干擾
                            
                        if content3:  # 假設 content 解析成功
                            logging.debug(f"讀取到的資料: {content3}")
                            break  # 解析成功，跳出迴圈
                        
                        if time.time() - start_time > timeout:  # 超時檢查
                            return "等待超時，無法取得足夠的資料"

                        time.sleep(0.1)  # 稍微等待，減少忙碌輪詢
                    except FileNotFoundError:
                        logging.error("文件不存在，等待寫入...")
                        time.sleep(0.1)  # 等待一段時間再嘗試

                # 假設 content 已經解析成功
                try:
                    contents3 = json.loads(content3)  # 嘗試解析 JSON
                except json.JSONDecodeError as e:
                    return f"無法解析 JSON 資料: {e}"
                
                #輸入辨識結果
                x=face.face(contents3)
                # 輸入結果
                response = model.generate_content("使用者的前方有:"+x+"此為使用者前方的辨識出的人，請根據此回答問題，請回答完整句子，回答問題時請以「您」稱呼使用者，如果畫面中沒有該人，就請回答沒有。例如:使用者詢問:我的前方有誰。請回答:您的前方有(畫面中出現的人)。接下來為問題:"+self.question)
                return(response.text)
        #其他類
        for keyword in keywordd:
            if keyword in self.distribution:
                response = model.generate_content(self.question)
                return(response.text)

   
               


    def img_object(self,img):
        data = json.loads(img)
        with open('img_object.txt', 'w') as file:
            file.write(json.dumps(data, indent=4)) 

    def img_face(self,img):
        data = json.loads(img)
        with open('img_face.txt', 'w') as file:
            file.write(json.dumps(data, indent=4))  

    def img_point(self,img):
        data = json.loads(img)
        with open('img_point.txt', 'w') as file:
            file.write(json.dumps(data, indent=4)) 

        # #判斷
        # keyworda = ["標點類問題"]
        # keywordb = ["物品類問題"]
        # keywordc = ["人物類問題"]
        # keywordd = ["其他類問題"]

        # self.distribution= response.text
        # #標點類
        # for keyword in keyworda:
        #     if keyword in self.distribution:
        #         return(f"請將手機對準地板五秒鐘")
               
             
        # #物品類
        # for keyword in keywordb:
        #     logging.debug(keywordb)
        #     if keyword in self.distribution:
        #         return(f"正在幫您開啟物品辨識功能，請將手機鏡頭對準想辨識的方向5秒鐘")
               
                
        # #人物類
        # for keyword in keywordc:
        #     if keyword in self.distribution:
        #         return(f"正在幫您開啟人臉功能，請將手機鏡頭對準想辨識的方向5秒鐘")
                
                
        # #其他類
        # for keyword in keywordd:
        #     if keyword in self.distribution:
        #         response = model.generate_content(question)
        #         return(response.text)

           






