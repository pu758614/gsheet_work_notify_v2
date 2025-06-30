import os
import json
import openai
from django.conf import settings
from example.sheet_lib import googleSheet
import datetime

class GptLib:
    def __init__(self):
        # 設定 OpenAI API 金鑰
        openai.api_key = settings.OPENAI_API_KEY

    def get_context_from_sheet(self):
        """從 Google Sheet 獲取當前年份的服事資料和使用者資料，作為 GPT 的上下文"""
        now_year = datetime.datetime.now().strftime('%Y')
        now_date = datetime.datetime.now()
        user_sheet = googleSheet('user')
        year_sheet = googleSheet(now_year)

        # 獲取所有使用者資料
        user_data = user_sheet.read_sheet_all()

        # 獲取當前年份的服事資料
        service_data = year_sheet.read_sheet_all()

        # 整理資料為適合 GPT 的格式
        context = {
            "users": [],
            "services": []
        }

        # 處理使用者資料
        for row in user_data:
            if len(row) >= 4:  # 確保資料完整
                user_info = {
                    "user_id": row[0],
                    "user_name": row[1],
                    "service_names": row[2].split('.') if len(row) > 2 and row[2] else [],
                    "notify_day": int(row[3]) if len(row) > 3 and row[3].isdigit() else 0
                }
                context["users"].append(user_info)

        # 處理服事資料
        from example.conf import field_code_conf
        for row in service_data:
            if len(row) > 0:
                service_date = row[0]
                if not self._is_date(service_date):
                    continue

                # 將服事日期轉換為 datetime 對象進行比較
                try:
                    # 解析 mm/dd 格式的日期，加上當前年份
                    date_parts = service_date.split('/')
                    service_datetime = datetime.datetime(now_date.year, int(date_parts[0]), int(date_parts[1]))

                    # 如果日期已過期，則跳過
                    if service_datetime < now_date:
                        continue

                    service_info = {
                        "date": service_date,
                        "services": []
                    }

                    for index, person in enumerate(row[1:], 1):
                        if person:
                            field_code = chr(65 + index)
                            if field_code in field_code_conf:
                                service_type = field_code_conf[field_code]
                                service_info["services"].append({
                                    "type": service_type,
                                    "person": person
                                })

                    context["services"].append(service_info)
                except ValueError:
                    # 日期解析錯誤，跳過此行
                    continue

        return context

    def _is_date(self, date_str):
        """檢查字串是否為日期格式 (mm/dd)"""
        try:
            datetime.datetime.strptime(date_str, '%m/%d')
            return True
        except ValueError:
            return False

    def query_gpt(self, user_message, user_id=None, user_name=None):
        """查詢 GPT 並獲取回應"""
        try:
            # 獲取上下文資料
            context_data = self.get_context_from_sheet()

            # 如果提供了使用者資訊，篩選相關資料
            user_specific_data = {}
            if user_id:
                user_specific_data = self._filter_user_data(context_data, user_id, user_name)

            # 組合提示詞
            system_prompt = """
            你是一個協助基督教會服事的AI助理，名叫「服事提醒小天使」。你可以回答關於教會服事的相關問題。
            請保持友善、專業的語氣，並在回答結尾使用適當的表情符號增加親和力。
            """
            # system_prompt = """
            # 你是一個協助基督教會服事的AI助理，名叫「服事提醒小天使」。你可以回答關於教會服事的相關問題。
            # 你應該根據提供的上下文資料來回答問題，但如果問題超出了上下文範圍，你可以提供一般性的建議或請求更多資訊。
            # 請保持友善、專業的語氣，並在回答結尾使用適當的表情符號增加親和力。
            # """

            # 組合上下文資料為文字
            context_text = json.dumps(user_specific_data if user_specific_data else context_data, ensure_ascii=False)

            # 創建完整提示詞
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "system", "content": f"這是目前的服事資料和使用者資料：{context_text}"},
                {"role": "user", "content": user_message}
            ]

            # 呼叫 OpenAI API
            response = openai.ChatCompletion.create(
                model="gpt-4",  # 可以根據需要替換為其他模型
                messages=messages,
                max_tokens=1000,
                temperature=0.7
            )

            # 獲取 GPT 的回應
            return response.choices[0].message.content

        except Exception as e:
            print(f"GPT API 呼叫失敗: {str(e)}")
            return f"抱歉，我現在無法回應您的問題。請稍後再試。(錯誤: {str(e)[:100]}...)"

    def _filter_user_data(self, context_data, user_id, user_name=None):
        """篩選特定使用者的相關資料"""
        result = {
            "users": [],
            "services": []
        }

        # 尋找使用者資料
        user_info = None
        for user in context_data["users"]:
            if user["user_id"] == user_id:
                user_info = user
                result["users"].append(user)
                break

        # 如果沒找到使用者資料但有提供名稱，創建一個基本資料
        if not user_info and user_name:
            user_info = {
                "user_id": user_id,
                "user_name": user_name,
                "service_names": [],
                "notify_day": 0
            }
            result["users"].append(user_info)

        # 如果找到使用者資料，篩選相關的服事資料
        if user_info and user_info["service_names"]:
            service_names = user_info["service_names"]
            for service_entry in context_data["services"]:
                relevant_services = []
                for service in service_entry["services"]:
                    # 檢查此服事是否與使用者相關
                    if service["person"] in service_names or any(name in service["person"] for name in service_names):
                        relevant_services.append(service)

                if relevant_services:
                    result["services"].append({
                        "date": service_entry["date"],
                        "services": relevant_services
                    })

        return result
