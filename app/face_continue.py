import json
import google.generativeai as genai
import os
import logging

# 設定 logging 格式
logging.basicConfig(format='%(asctime)s - %(message)s - [%(funcName)s:%(lineno)d]', level=logging.DEBUG)

api_key = 'AIzaSyBCcg0skdWwwG-hBucIvDCLHY9FFtzw9-0'
genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-pro')

history="無"
count=0

def facecon(input_data):
    global history
    global count
    # input_data = json.loads(data)
    # 假設有一個名為 .txt 的文件
    with open('target.txt', 'r', encoding='utf-8') as file:
        content = file.read()

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
    ans = "使用者的視野裡有" + result
    # print(ans)
    # first=model.generate_content("請幫我篩選出使用者關注目標的資訊，請幫我過濾掉關注對象以外的資訊。以下兩個情況為參考回答示範。示範1:示範題目:使用者的視野裡有Huang、Paney、Irene。使用者的關注目標:Irene。在這個情況中請幫我過濾掉Irene以外的人物，因此需回答:關注對象Irene出現在您的視野中。示範題目2:使用者的視野裡有Paney、Irene。使用者的關注目標:Huang。在這個情況中請幫我過濾掉Huang以外的人物資訊，因此需回答:您的視野裡沒有關注對象Huang。請注意，以上只是範例，一切資訊包括使用者視野裡有甚麼跟關注對象皆以接下來的題目為準，尤其是關注目標，請必定要依照接下來後面題目的關注目標篩選題目資訊，非關注目標的資訊一律都必須過濾掉。只需要給我最終的回答就好，不需要有多餘的過程。接下來為正式題目:"+ans+"。使用者的關注目標:"+target)
    first=model.generate_content("請幫我篩選出使用者關注目標的資訊，請幫我過濾掉關注對象以外的資訊。非關注目標的資訊一律都必須過濾掉，只需要專注回答使用者關注對象的資訊就好。舉個例子:假設題目說:使用者的視野裡有Paney、Huang。使用者關注的目標為Paney。解題思路:例題中使用者的關注目標為Paney，因此只須回答關注對象Paney的資訊就好，此例題中關注對象以外的Huang就要過濾掉，因此最終只須回答「使用者的視野中有關注對象Paney」。再舉個例子:假設這次題目說:使用者的視野裡有Huang。使用者關注的目標為Irene、Huang。解題思路:這次例題中使用者的關注目標為Irene跟Huang，因此須回答關注對象Irene和Huang的資訊，此例題中關注對象Huang有出現在使用者的視野中，而Irene沒有，則須回報給使用者「使用者的視野中有關注對象Huang，沒有關注對象Irene」。請記住，剛剛的只是例題，你只能參考它的解題思路，每個題目視野中出線的人跟關注對象都有可能改變，所以接下來一切的回答都以後面的正是題目為準。這是你剛剛的回答錯誤案例，在這個案例中:使用者的視野裡有Paney。使用者的關注目標:Irene、Huang、Paney。你在這個案例中的錯誤回答:使用者的視野中有關注對象 Huang 和 Paney，沒有關注對象 Irene。訂正:在這個案例中，使用者的視野中只有Paney，並沒有Huang，回答請完全依據使用者的視野中有的人，因此在這個案例中，答案應該為:使用者的視野中有關注對象Paney，沒有關注對象Huang跟Irene。請記得在之後得回答中避免該錯誤再次發生。只需要給我最終的回答就好，不需要有多餘的過程。接下來為正式題目:"+ans+"。使用者的關注目標:"+content)
    # print("過去:"+history+"\n現在:"+first.text)
    sec=model.generate_content("請幫我比對過去跟現在兩筆資料回應給使用者，如果過去資料為無，即回答現在資料，如果過去資料存在，則需告訴使用者和過去資料相比，使用者的視野出現了甚麼變化，如果資料中沒有提到某人，即代表某人目前不在使用者的視野範圍中，請回報畫面中沒有該人。接下來為例題:過去資料:使用者的視野中有關注對象 Irene 現在資料:使用者的視野中有關注對象 Paney 解題思路:在例題的情況中，使用者目前的視野中少了關注對象 Irene，多了關注對象 Paney，你需要回答給使用者視野中出現了甚麼變化，因此在例題中應該回答:關注對象Irene離開了您的視野，關注對象Paney出現在了您的視野中。請記住，剛剛的只是參考用的例題，你只能參考它的解題思路，正式回答請完全根據後面的現在資料即過去資料。我最後只需要回報給使用者的回答，如果現在資料跟現在資料之間完全沒有變化，回答一定要包含關鍵字:沒有變化，反之，如果有任何一物品出現變化，則不能包含關鍵字:沒有變化。這是你關於「沒有變化」的錯誤回答案例，案例中過去資料:使用者的視野中有關注對象 Huang，沒有 Irene 和 Paney。現在資料:使用者的視野中有關注對象Paney，沒有關注對象Huang和Irene。你在這個案例中的錯誤回答:您現在的視野中出現了一位新的關注對象：Paney，而過去視野中的關注對象 Huang 離開了您的視野，沒有變化。訂正:使用者的視野中出現了Paney，少了Huang，有發生改變，因此你不能在回答中提到「沒有變化」，請記住這屬於嚴重的錯誤，因此，在這個案例中你應該回答:關注對象Paney出現在了您的視野，關注對象Huang離開了的視野 。接下來為「」內的為例題:「過去資料:使用者的視野中有關注對象 Huang 。現在資料:使用者的視野中有關注對象Huang。，解題思路:由於現在資料跟過去資料之間沒有改變，因此在這個例題中最終應回答:您現在的視野中有關注對象Huang，沒有變化」。這是你剛剛的回答錯誤案例，在這個案例中，過去資料:使用者的視野中有關注對象Huang。現在資料:使用者的視野中沒有關注對象Huang。你在錯誤案例中的錯誤回答為:您現在的視野中不再關注對象Huang。修正:請記住案例中提到的沒有關注對象指的是，沒有了，關注對象Huang；並不是不再關注Huang的意思，因此你在這個案例中，應該回答:關注對象Huang離開了您的視野。這是第二個錯誤案例，在這個案例中，過去資料:使用者的視野中有關注對象 Huang 和 Paney，沒有關注對象 Irene。現在資料:使用者的視野中有關注對象 Paney。在這個錯誤案例中，你當時的回答為:關注對象 Irene 和 Huang 都離開了您的視野。修正:請記得，你只需要比較現在資料跟過去資料的變化，在這個案例中，過去資料提到使用者的視野裡只有Paney跟Huang，沒有Irene，而現在資料只剩下Paney，和過去資料相比使用者的視野只少了Huang，在這個案例中，過去使用者的視野中有Paney跟Huang，現在使用者的視野中有Paney，兩者相比較只少了Huang，因此在這個案例中，你的回答應該為:關注對象Huang離開了您的視野。請記得在之後得回答中避免該錯誤再次發生。回答時請記得以「您」來稱呼使用者，接下來，為正式的題目:過去資料:"+history+" 。現在資料:"+first.text)
    # print("b:"+sec.text)
    final=sec.text
    keyword = ["沒有變化"]
    for keyword in keyword:
        if keyword in final:
            #這邊能改變重複次數
            if count<=3:
                final=" "
                count+=1
                break
            else:
                count=0
    # print("a"+final)

    history=first.text
    logging.debug(final)
    return final


a = [
    {"name": "Paney", "confidence": 0.6877386840481583},
    {"name": "Huang", "confidence": 0.6877386840481583}
]
b = [
    {"name": "Huang", "confidence": 0.6877386840481583}
]
c = [
    {"name": "Paney", "confidence": 0.6877386840481583},
]
d = [
    {"name": "Irene", "confidence": 0.6877386840481583}
]
e = [
    {"name": "Paney", "confidence": 0.6877386840481583},
]
















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