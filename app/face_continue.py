import json
import os
import logging
from . import geminimodule

# 設定 logging 格式
logging.basicConfig(format='%(asctime)s - %(message)s - [%(funcName)s:%(lineno)d]', level=logging.DEBUG)



with open('target.txt', 'r', encoding='utf-8') as file:
    content = file.read()
history="無"
count=0

def facecon(data):
    global history
    global count
    global content
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
    ans = "使用者的視野裡有" + result
    # print(ans)
    # first=model.generate_content("請幫我篩選出使用者關注目標的資訊，請幫我過濾掉關注對象以外的資訊。以下兩個情況為參考回答示範。示範1:示範題目:使用者的視野裡有Huang、Paney、Irene。使用者的關注目標:Irene。在這個情況中請幫我過濾掉Irene以外的人物，因此需回答:關注對象Irene出現在您的視野中。示範題目2:使用者的視野裡有Paney、Irene。使用者的關注目標:Huang。在這個情況中請幫我過濾掉Huang以外的人物資訊，因此需回答:您的視野裡沒有關注對象Huang。請注意，以上只是範例，一切資訊包括使用者視野裡有甚麼跟關注對象皆以接下來的題目為準，尤其是關注目標，請必定要依照接下來後面題目的關注目標篩選題目資訊，非關注目標的資訊一律都必須過濾掉。只需要給我最終的回答就好，不需要有多餘的過程。接下來為正式題目:"+ans+"。使用者的關注目標:"+target)
    first=geminimodule.model.generate_content("請幫我篩選出使用者關注目標的資訊，請幫我過濾掉關注對象以外的資訊。非關注目標的資訊一律都必須過濾掉，只需要專注回答使用者關注對象的資訊就好。舉個例子:假設題目說:使用者的視野裡有Paney、Huang。使用者關注的目標為Paney。解題思路:例題中使用者的關注目標為Paney，因此只須回答關注對象Paney的資訊就好，此例題中關注對象以外的Huang就要過濾掉，因此最終只須回答「使用者的視野中有關注對象Paney」。再舉個例子:假設這次題目說:使用者的視野裡有Huang。使用者關注的目標為Irene、Huang。解題思路:這次例題中使用者的關注目標為Irene跟Huang，因此須回答關注對象Irene和Huang的資訊，此例題中關注對象Huang有出現在使用者的視野中，而Irene沒有，則須回報給使用者「使用者的視野中有關注對象Huang，沒有關注對象Irene」。請記住，剛剛的只是例題，你只能參考它的解題思路，每個題目視野中出線的人跟關注對象都有可能改變，所以接下來一切的回答都以後面的正是題目為準。這是你剛剛的回答錯誤案例，在這個案例中:使用者的視野裡有Paney。使用者的關注目標:Irene、Huang、Paney。你在這個案例中的錯誤回答:使用者的視野中有關注對象 Huang 和 Paney，沒有關注對象 Irene。訂正:在這個案例中，使用者的視野中只有Paney，並沒有Huang，回答請完全依據使用者的視野中有的人，因此在這個案例中，答案應該為:使用者的視野中有關注對象Paney，沒有關注對象Huang跟Irene。請記得在之後得回答中避免該錯誤再次發生。只需要給我最終的回答就好，不需要有多餘的過程。接下來為正式題目:"+ans+"。使用者的關注目標:"+content)
    # print("過去:"+history+"\n現在:"+first.text)
    sec=geminimodule.model.generate_content("請幫我比對過去跟現在兩筆資料回應給使用者，如果過去資料為無，即回答現在資料，如果過去資料存在，則需告訴使用者和過去資料相比，使用者的視野出現了甚麼變化，如果資料中沒有提到某人，即代表某人目前不在使用者的視野範圍中，請回報畫面中沒有該人。接下來為例題:過去資料:使用者的視野中有關注對象 Irene 現在資料:使用者的視野中有關注對象 Paney 解題思路:在例題的情況中，使用者目前的視野中少了關注對象 Irene，多了關注對象 Paney，你需要回答給使用者視野中出現了甚麼變化，因此在例題中應該回答:關注對象Irene離開了您的視野，關注對象Paney出現在了您的視野中。請記住，剛剛的只是參考用的例題，你只能參考它的解題思路，正式回答請完全根據後面的現在資料即過去資料。我最後只需要回報給使用者的回答，如果現在資料跟現在資料之間完全沒有變化，回答一定要包含關鍵字:沒有變化，反之，如果有任何一物品出現變化，則不能包含關鍵字:沒有變化。這是你關於「沒有變化」的錯誤回答案例，案例中過去資料:使用者的視野中有關注對象 Huang，沒有 Irene 和 Paney。現在資料:使用者的視野中有關注對象Paney，沒有關注對象Huang和Irene。你在這個案例中的錯誤回答:您現在的視野中出現了一位新的關注對象：Paney，而過去視野中的關注對象 Huang 離開了您的視野，沒有變化。訂正:使用者的視野中出現了Paney，少了Huang，有發生改變，因此你不能在回答中提到「沒有變化」，請記住這屬於嚴重的錯誤，因此，在這個案例中你應該回答:關注對象Paney出現在了您的視野，關注對象Huang離開了的視野 。接下來為「」內的為例題:「過去資料:使用者的視野中有關注對象 Huang 。現在資料:使用者的視野中有關注對象Huang。，解題思路:由於現在資料跟過去資料之間沒有改變，因此在這個例題中最終應回答:您現在的視野中有關注對象Huang，沒有變化」。這是你剛剛的回答錯誤案例，在這個案例中，過去資料:使用者的視野中有關注對象Huang。現在資料:使用者的視野中沒有關注對象Huang。你在錯誤案例中的錯誤回答為:您現在的視野中不再關注對象Huang。修正:請記住案例中提到的沒有關注對象指的是，沒有了，關注對象Huang；並不是不再關注Huang的意思，因此你在這個案例中，應該回答:關注對象Huang離開了您的視野。這是第二個錯誤案例，在這個案例中，過去資料:使用者的視野中有關注對象 Huang 和 Paney，沒有關注對象 Irene。現在資料:使用者的視野中有關注對象 Paney。在這個錯誤案例中，你當時的回答為:關注對象 Irene 和 Huang 都離開了您的視野。修正:請記得，你只需要比較現在資料跟過去資料的變化，在這個案例中，過去資料提到使用者的視野裡只有Paney跟Huang，沒有Irene，而現在資料只剩下Paney，和過去資料相比使用者的視野只少了Huang，在這個案例中，過去使用者的視野中有Paney跟Huang，現在使用者的視野中有Paney，兩者相比較只少了Huang，因此在這個案例中，你的回答應該為:關注對象Huang離開了您的視野。請記得在之後得回答中避免該錯誤再次發生。回答時請記得以「您」來稱呼使用者，接下來，為正式的題目:過去資料:"+history+" 。現在資料:"+first.text)
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
