import json
import google.generativeai as genai
import os
import logging

logging.basicConfig(format='%(asctime)s - %(message)s - [%(funcName)s:%(lineno)d]', level=logging.DEBUG)


def face(input_data):
   
    item_counts = {
        "Huang": 0,
        "Irene": 0,
        "Paney": 0,
    }
    
    # 確保 input_data 是可迭代的
    for item in input_data:
        if isinstance(item, dict):
            if item["name"] == "Huang" and item["confidence"] > 0.1:
                item_counts["Huang"] += 1
            elif item["name"] == "Irene" and item["confidence"] > 0.1:
                item_counts["Irene"] += 1
            elif item["name"] == "Paney" and item["confidence"] > 0.1:
                item_counts["Paney"] += 1
    
    # 只保留數量大於 0 的項目
    fitem = {item: count for item, count in item_counts.items() if count > 0}
    
    # 構建結果字符串，僅包含物品名稱
    result = "、".join(f"{item}" for item in fitem.keys())
    logging.debug(result)
    ans = "畫面中有" + result
    return ans

