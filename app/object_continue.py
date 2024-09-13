import json
from . import geminimodule
import os
import logging

# 設定 logging 格式
logging.basicConfig(format='%(asctime)s - %(message)s - [%(funcName)s:%(lineno)d]', level=logging.DEBUG)






history = "無"
count = 0


def con(data):
    global history
    global count
    # 假設有一個名為 .txt 的文件
    with open('target.txt', 'r', encoding='utf-8') as file:
        content = file.read()
    input_data = json.loads(data)
    item_counts = {
        "本書": 0,
        "個水壺": 0,
        "張椅子": 0,
        "張桌子": 0,
        "台筆電": 0,
        "枝筆": 0
    }
    
    # 定義物品名稱與對應中文的映射
    item_mapping = {
        "Book": "本書",
        "Bottle": "個水壺",
        "Chair": "張椅子",
        "Desk": "張桌子",
        "Laptop": "台筆電",
        "Pen": "枝筆"
    }
    
    # 篩選出 confidence > 0.3 的物品
    for item in input_data:
        if isinstance(item, dict):
            name = item.get("name")
            confidence = item.get("confidence", 0)
            
            if name in item_mapping and confidence > 0.1:
                item_counts[item_mapping[name]] += 1
    
    # 將結果轉換為新的字典
    fitem = {item: count for item, count in item_counts.items()}
    
    # 構建結果字符串，包含物品名稱和數量
    result = "、".join(f"{count}{item}" for item, count in fitem.items())
    ans = "使用者的視野裡有" + result
    
    # first=geminimodule.model.generate_content("請幫我篩選出使用者關注目標的資訊，請幫我過濾掉關注對象以外的資訊。以下兩個情況為參考回答示範。示範1:示範題目:使用者的視野裡有1本書、0個水壺、5張椅子、0張桌子、0台筆電、2枝筆。使用者的關注目標:書、筆電、筆。在這個情況中請幫我過濾掉書、筆電、筆以外的物品資訊，因此需回答:使用者的的視野裡有1本書、0台筆電、2枝筆。示範題目2:使用者的視野裡有1本書、0個水壺、6張椅子、1張桌子、0台筆電、1枝筆。使用者的關注目標:桌子、椅子、筆電。在這個情況中請幫我過濾掉桌子、椅子、筆電以外的物品資訊，因此需回答:使用者的視野裡有1張桌子、6張椅子、0台筆電。這個是你剛剛回答錯誤的結果，也就是錯誤示範，請在之後的回答改正這個錯誤:使用者的視野裡有1本書、0個水壺、6張椅子、1張桌子、0台筆電、1枝筆 使用者的關注目標:筆。你的回答:使用者的視野裡有1本書、0台筆電、1枝筆。由於使用者在這個示範中並沒有關注筆電跟書，你的回答就必須把書跟筆電的資訊過濾掉，正確回答應該是:使用者的視野裡有1枝筆。請注意，以上只是範例，一切資訊包括使用者視野裡有甚麼跟關注對象皆以接下來的題目為準，尤其是關注目標，請必定要依照接下來後面題目的關注目標篩選題目資訊，非關注目標的資訊一律都必須過濾掉。只需要給我最終的回答就好，不需要有多餘的過程。接下來為正式題目:"+ans+"。使用者的關注目標:"+ content)
    #print("過去:" + history + "\n現在:" + first.text)
    
    # sec=geminimodule.model.generate_content("請幫我比對過去跟現在兩筆資料回應給使用者，如果過去資料為無，即回答現在資料，如果過去資料存在，則告訴使用者和過去資料相比，使用者的視野出現了甚麼變化，如果物品數量為0，請回報畫面中沒有該物品。接下來3個情況為回答參考，情況1:過去資料:無 現在資料:使用者的視野裡有0個水壺、5張椅子。因為水壺數量為0，因此最終須回答:[您的視野中有五張椅子，沒有水壺]。情況2:過去資料:使用者的視野裡有0個水壺、5張椅子 現在資料:使用者的視野裡有0個水壺、5張椅子。因為和過去資料相比，現在的資料沒有變化，，因此最終須回答:[您視野中的畫面沒有變化]。情況2:過去資料:使用者的視野裡有0個水壺、5張椅子 現在資料:使用者的視野裡有2個水壺、4張椅子。因為和過去資料相比，使用者的視野多了2個水壺，少了一張椅子，因此須回報給使用者環境的改變，因此最終須回答:[您的視野中多出了兩個水壺，有一張椅子離開了您的視野]，請記住，這三個參考情況為範例，接下來請根據後面輸入的現在資料跟過去資料，依照範例的方式回答使用者。我最後只需要回報給使用者的回答，如果現在資料跟現在資料之間完全沒有變化，回答一定要包含關鍵字:沒有變化，反之，如果有任何一物品出現變化，則不能包含關鍵字:沒有變化。過去資料:"+history+" 現在資料:"+first.text)
    # print("b:" + sec.text)
    sec = geminimodule.model.generate_content("請幫我檢查 result 中的項目，並比較它們是否與 content 中的項目相同。如果 result 中的項目與 content 中數量大於 0 的某些項目相符，請回答該些項目出現在您的視野範圍。例如1：如果 result 是筆、椅子，而 content 是 0 本書、0 個水壺、0 張椅子、0 張桌子、0 台筆電、1 枝筆，請回答「1 枝筆出現在您的視野範圍」。例如2：如果 result 是筆、椅子，而 content 是 0 本書、0 個水壺、3 張椅子、0 張桌子、0 台筆電、1 枝筆，請回答「3 張椅子和1 枝筆出現在您的視野範圍」。如果 result 中沒有任何符合 content 的項目或 result 為空，則回答「  」，請注意不要出現其他回答。以下是正式數據：result："+result+"。content:"+content)
    #N=geminimodule.model.generate_content("請根據以下規則比對過去資料和現在資料，並回應給使用者：1. 如果過去資料為空（「 」），請直接回應現在資料。2. 如果過去資料存在：- 比對過去資料和現在資料。- 如果現在資料和過去資料完全相同，回應「  」。如果有變化：- 如果過去資料中的物品在現在資料中數量為0，回應該物品已脫離視線。- 如果現在資料中出現新的物品，回應這些物品現在出現在視野範圍內。- 對於其他變化，描述具體的變化情況。以下是三個參考情況：

    final = sec.text
     # 檢查 sec 是否為 None 或 sec.text 是否為空
    if sec is None or not sec.text.strip():
        return ""  # 返回空字符串，表示沒有任何內容
    
    # 處理包含關鍵字 "沒有變化" 的情況
    # if "沒有變化" in final and count <= 3:
    #     final = " "
    #     count += 1
    # else:
    #     count = 0
    
    # 更新歷史數據
    # history = first.text
    logging.debug(final)
    return final
    

