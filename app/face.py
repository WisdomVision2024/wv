import json
import google.generativeai as genai
import os

api_key = 'AIzaSyBCcg0skdWwwG-hBucIvDCLHY9FFtzw9-0'
genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-pro')

def face(data):
    input_data = json.loads(data)
    item_counts = {
        "Huang": 0,
        "Irene": 0,
        "Paney": 0,
    }
    
    # 確保 input_data 是可迭代的
    for item in input_data:
        if isinstance(item, dict):
            if item["name"] == "Huang" and item["confidence"] > 0.5:
                item_counts["Huang"] += 1
            elif item["name"] == "Irene" and item["confidence"] > 0.5:
                item_counts["Irene"] += 1
            elif item["name"] == "Paney" and item["confidence"] > 0.5:
                item_counts["Paney"] += 1
    
    # 只保留數量大於 0 的項目
    fitem = {item: count for item, count in item_counts.items() if count > 0}
    
    # 構建結果字符串，僅包含物品名稱
    result = "、".join(f"{item}" for item in fitem.keys())
    ans = "畫面中有" + result
    return ans

# 測試資料
a = [
    {"name": "Huang", "confidence": 0.6877386840481583}
]
b = [
    {"name": "Paney", "confidence": 0.6877386840481583},
]
c = [
    {"name": "Paney", "confidence": 0.6877386840481583},
]
d = [
    {"name": "Paney", "confidence": 0.6877386840481583},
]
e = [
    {"name": "Paney", "confidence": 0.6877386840481583},
]

# x=("結果一:"+face(a)+"\n，結果二:"+face(b)+ "\n，結果三:"+face(c)+"\n，結果四:"+face(d)+"\n，結果五:"+face(e))
# print(x)
# response = model.generate_content("現在一共有三個人，分別是Huang、Irene、Paney，接下來會有五個結果敘述出畫面中這三個人是否存在，每一個人都有存在跟不存在兩個狀態，畫面中沒有提到即代表不存在，同一個人在不同結果中可能會有不同狀態，請綜合所有結果，以多數為真的邏輯，只要一個結果出現次出在三次以上即為真，整合出最終答案，以下中括號中的文字為例題:[結果一:畫面中有Huang、Paney，結果二:畫面中有Huang、Paney，結果三:畫面中有Huang，結果四:畫面中有Irene、Paney，結果五:畫面中有Irene、Paney]以下中括號部分為思考過程，接下來請完全參考此過程作答[判斷Huang:三個結果中Huang存在，兩個結果顯示Huang不存在，因為Huang存在出現了三次，所以判斷Huang存在為真，所以判斷畫面中有Huang；判斷Irene:兩個結果中Irene存在，三個結果顯示Irene不存在，因為Irene不存在的結果在三以上，所以判斷畫面中沒有Irene，由於Irene不存在，則最後答案中不用顯示；判斷Paney:四個結果中Paney存在，一個結果顯示Paney不存在，因為最多結果顯示Paney存在，顯示Paney存在的結果在三以上，所以判斷畫面中有Paney；判斷完所有物品即可整合出答案:畫面中有Huang、Paney。以下為題目，請參考剛剛的思考流程整合結果，再次強調，我需要的是重複次數最多的答案，這是你剛剛的錯誤案例；結果一:畫面中有Irene，結果二:畫面中有Irene，結果三:畫面中有Irene，結果四:畫面中有Huang、Paney，結果五:畫面中有Irene、Paney。你的錯誤回答為:畫面中有Huang，依照案例中五個結果，根據多數為真的邏輯，正確回答應該是:畫面中有Irene。錯誤案例2:結果一:畫面中有Huang，結果二:畫面中有Huang，結果三:畫面中有Irene，結果四:畫面中有Huang，結果五:畫面中有Irene、Paney。你的錯誤回答:畫面中有Irene，根據多數為真，案例中三個結果Huang存在，三個結果Irene不存在，四個結果Paney不存在，以上為真，當不存在的結果的數量在三以上時，就不要回報給使用者，因此答案應該為:畫面中有Huang。請記住，剛剛的只是例子，只能參考案例中答題的答題邏輯，接下來請根據這個答題邏輯幫我隱藏過程，回答現在的情況:"+x)
# print(response.text)
# q=input("輸入問題:")
# response = model.generate_content("Paney、Huang、Irene皆為使用者認識的人，例如使用者可能會問:Paney在我的前面嗎，如果畫面中有Paney的話，就要回答，是的Paney在您的前面。請根據此回答問題，請回答完整句子，如果畫面中沒有該人，就請回答沒有。這是你剛剛的錯誤案例:在這個案例中的畫面中有Huang、Paney，案例的問題為:這附近有我認識的人嗎，你的錯誤回答為:是的，Paney在您的前面。在你的回答中，你忽略了Huang也在你的畫面中，他們三個都是使用者認識的人，因此只要有出現就要回報給使用者，畫面中沒提到Irene，代表他不存在，因此正確的回答為:有，Huang跟Paney在您的前方。此為剛剛的對話紀錄:現在畫面中有Huang、Paney。問題:誰在我的前方。你的回答:Paney在您的前方，看起來你又忽略了畫面中有的Huang，請記住，只要畫面中有提到的都必須回報給使用者，之後請記得修正這個問題，正確回答應該為:目前Paney跟Huang在您的前方。請記住，剛剛的只是例子，只能參考案例中答題的邏輯，接下來請根據畫面中的資訊「現在"+response.text+"」來回答問題，此為使用者前方的畫面，現在使用者的問題為:"+q)
# print(response.text)