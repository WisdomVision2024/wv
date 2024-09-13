import json
import google.generativeai as genai
import os
import logging

# 設定 logging 格式
logging.basicConfig(format='%(asctime)s - %(message)s - [%(funcName)s:%(lineno)d]', level=logging.DEBUG)


api_key = 'AIzaSyBCcg0skdWwwG-hBucIvDCLHY9FFtzw9-0'
genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-pro')   

def look(data):
        response = model.generate_content("請判斷使用者想關注下列三個人中的哪幾位以及下列六項物品中的哪幾項並回答人物名稱或物品名稱，人物名稱有1.Huang2.Irene3.Paney，物品名稱有1.書2.水壺3.椅子4.桌子5.筆電6.筆，回答的人物名稱必須何上述一模一樣，包括大小寫。例如要求為:請幫我關注Huang和Paney，則回答Huang、Paney，例如要求為:請幫我關注書本和筆，則回答書、筆，例如要求為:請幫我關注Huang和椅子，則回答Huang、椅子。請注意，若關注對象不在以上人物名稱和物品名稱中，則刪除，例如:請幫我關注衣服和Paney，則回答Paney,例如:請幫我關注Kiki和電視，則回答。請記住，上面的只是例題，接下來的關注對象以使用者的要求為準。請注意，答案內容只會有以下選項Huang、Irene、Paney 、書、水壺、椅子、桌子、筆電、筆。請注意，問題可能會出現同音錯字，例如:我想關注比，使用者想表達的是:我想關注筆。使用者要求:"+data)
        target = response.text
        logging.debug(target)
        with open('target.txt', 'w') as file:
            file.write(target)  # 覆蓋寫入新內容
        return target