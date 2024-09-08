import json
import google.generativeai as genai
import os



def con(data):
    input_data = json.loads(data)
    item_counts = {
        "本書": 0,
        "個水壺": 0,  # 初始值
        "張椅子": 0,
        "張桌子": 0,   # 初始值
        "台筆電": 0,
        "枝筆": 0
    }
    # 確保 input_data 是可迭代的
    for item in input_data:
        if isinstance(item, dict):
            if item["name"] == "Book" and item["confidence"] > 0.6:
                item_counts["本書"] += 1
            elif item["name"] == "Bottle" and item["confidence"] > 0.6:
                item_counts["個水壺"] += 1
            elif item["name"] == "Chair" and item["confidence"] > 0.6:
                item_counts["張椅子"] += 1
            elif item["name"] == "Desk" and item["confidence"] > 0.6:
                item_counts["張桌子"] += 1
            elif item["name"] == "Laptop" and item["confidence"] > 0.6:
                item_counts["台筆電"] += 1
            elif item["name"] == "Pen" and item["confidence"] > 0.6:
                item_counts["枝筆"] += 1
    # 只保留數量大於 0 的項目
    fitem = {item: count for item, count in item_counts.items() if count > 0}
    
    # 構建結果字符串，包含物品名稱和數量
    result = "、".join(f"{count}{item}" for item, count in fitem.items())
    print("result:"+result)
    ans="畫面中有"+result
    return ans







