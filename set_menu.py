import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE","api.settings")
django.setup()

import requests
import json
from django.conf import settings
from linebot import LineBotApi, WebhookParser

# 設定 headers，輸入你的 Access Token，記得前方要加上「Bearer 」( 有一個空白 )
access_token = settings.LINE_CHANNEL_ACCESS_TOKEN
headers = {'Authorization':f"Bearer {access_token}",'Content-Type':'application/json'}

body = {
    'size': {'width': 2498, 'height': 928},   # 設定尺寸
    'selected': 'true',                        # 預設是否顯示
    'name': 'Richmenu demo',                   # 選單名稱
    'chatBarText': '請以週報.群組記事本的為主',            # 選單在 LINE 顯示的標題
    'areas':[                                  # 選單內容
        {
          'bounds': {'x': 0, 'y': 0, 'width': 314, 'height': 332}, # 選單位置與大小
          'action': {'type': 'message', 'text': '小天使, 請禮拜日提醒我'}                # 點擊後傳送文字
        },
        {
          'bounds': {'x': 315, 'y': 0, 'width': 309, 'height': 329}, # 選單位置與大小
          'action': {'type': 'message', 'text': '小天使, 請禮拜一提醒我'}                # 點擊後傳送文字
        },
        {
          'bounds': {'x': 633, 'y': 0, 'width': 309, 'height': 329}, # 選單位置與大小
          'action': {'type': 'message', 'text': '小天使, 請禮拜二提醒我'}                # 點擊後傳送文字
        },
        {
          'bounds': {'x': 941, 'y': 0, 'width': 309, 'height': 329}, # 選單位置與大小
          'action': {'type': 'message', 'text': '小天使, 請禮拜三提醒我'}                # 點擊後傳送文字
        },
        {
          'bounds': {'x': 1257, 'y': 0, 'width': 309, 'height': 329}, # 選單位置與大小
          'action': {'type': 'message', 'text': '小天使, 請禮拜四提醒我'}                # 點擊後傳送文字
        },
        {
          'bounds': {'x': 1567, 'y': 0, 'width': 309, 'height': 329}, # 選單位置與大小
          'action': {'type': 'message', 'text': '小天使, 請禮拜五提醒我'}                # 點擊後傳送文字
        },
        {
          'bounds': {'x': 1882, 'y': 0, 'width': 309, 'height': 329}, # 選單位置與大小
          'action': {'type': 'message', 'text': '小天使, 請禮拜六提醒我'}                # 點擊後傳送文字
        },
        {
          'bounds': {'x': 2190, 'y': 0, 'width': 309, 'height': 329}, # 選單位置與大小
          'action': {'type': 'message', 'text': '小天使, 請先不用提醒我'}                # 點擊後傳送文字
        },
        {
          'bounds': {'x': 837, 'y': 341, 'width': 832, 'height': 583}, # 選單位置與大小
          'action': {'type': 'message', 'text': '小天使, 請問我接下來服事有哪些?'}                # 點擊後傳送文字
        },
        {
          'bounds': {'x': 0, 'y': 338, 'width': 836, 'height': 590}, # 選單位置與大小
          'action': {'type': 'message', 'text': '小天使, 請問這怎麼用?'}                # 點擊後傳送文字
        },


    ]
  }


req = requests.request('POST', 'https://api.line.me/v2/bot/richmenu',
                      headers=headers,data=json.dumps(body).encode('utf-8'))
if req.status_code != 200:
    print('Step 1 error',req.text)
    exit()
rich_menu_id = req.json()['richMenuId']

file_path = "/code/richmenu.png"
# API端點
url = f"https://api-data.line.me/v2/bot/richmenu/{rich_menu_id}/content"

# 請求標頭
headers = {
    "Authorization": f"Bearer {access_token}",
    "Content-Type": "image/png"
}

with open(file_path, "rb") as file:
    response = requests.post(url, headers=headers, data=file)

# 檢查回應
if response.status_code == 200:
    print("成功上傳圖片到Line Rich Menu。")
else:
    print(f"Step 2 error: {response.status_code}")
    print(response.text)




headers = {'Authorization':f'Bearer {access_token}'}

req = requests.request('POST', f'https://api.line.me/v2/bot/user/all/richmenu/{rich_menu_id}', headers=headers)
if req.status_code != 200:
    print('Step 3 error',req.text)
    exit()
print(req.text)