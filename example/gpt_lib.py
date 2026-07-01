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
                user_specific_data = self._filter_user_data(
                    context_data, user_id, user_name)
            date = datetime.datetime.now().strftime('%Y/%m/%d')

            # 優化的 system prompt - 強調準確性和事實核查
            system_prompt = f"""你是「服事提醒小天使」，專門協助基督教會的服事排程管理AI助理。

**當前資訊:**
- 今天日期: {date}
- 發問者: {user_name}

**你的職責:**
1. 根據提供的服事表資料回答問題
2. 幫助教友查詢自己或他人的服事排程
3. 提供準確的日期和服事類型資訊

**嚴格準確性規則（最重要）:**
- 你只能根據下方提供的資料回答，絕對不可以猜測或編造
- 如果某個日期的某個服事欄位裡「沒有出現」該人的名字，就代表他在那天「沒有」該服事
- 判斷某人是否有服事時，必須逐一檢查該日期每個服事欄位的人員名單，名字必須完全吻合才算有排到
- 人員欄位中用「.」或「、」分隔代表多人，例如「雅慧.蔚均」代表兩個人：雅慧 和 蔚均
- 如果資料中找不到相關資訊，直接說「沒有找到相關資料」，不要自行推測
- 回答前請先在內心逐一核對資料，確認無誤後再回覆

**回答原則:**
- 優先使用「個人專屬資料」回答(如果有提供)
- 若個人資料不足，再參考「完整服事表」
- 日期格式為 mm/dd，請自動判斷年份(通常是今年或明年)
- 回答要具體明確，包含日期和服事類型
- 語氣友善專業
- 不需要建議繼續問答
- 回覆將顯示在 LINE 訊息中，LINE 不支援 Markdown，所以絕對不要使用 **粗體**、*斜體*、# 標題、- 列表 等 Markdown 語法，請用純文字格式回覆

**服事類型說明:**
{self._get_service_type_description()}
"""

            # 格式化個人專屬資料
            user_context = ""
            if user_specific_data and user_specific_data.get("services"):
                user_context = self._format_user_context(
                    user_specific_data, user_name)

            # 格式化完整服事表(作為參考)
            all_services = self._format_all_services(context_data['services'])

            # 創建完整提示詞 - 分層提供資料
            messages = [
                {"role": "system", "content": system_prompt}
            ]

            # 如果有個人資料，優先提供
            if user_context:
                messages.append({
                    "role": "system",
                    "content": f"**{user_name} 的個人專屬資料(優先使用此資料回答):**\n{user_context}"
                })

            # 提供完整服事表作為參考
            messages.append({
                "role": "system",
                "content": f"**完整服事表(作為參考，用於回答其他人的服事或統計問題):**\n{all_services}"
            })

            # 加入準確性範例(Few-shot learning) - 示範如何核對資料
            messages.extend([
                {"role": "user", "content": "7/11 我有沒有被排到服事？"},
                {"role": "assistant",
                    "content": f"{user_name}您好，我幫您核對了 7/11 的服事表：\n\n我逐一檢查了 7/11 當天所有服事欄位，您的名字沒有出現在任何欄位中。\n\n所以 7/11 您沒有被排到服事。"},
                {"role": "user", "content": "那 7/25 呢？"},
                {"role": "assistant",
                    "content": f"{user_name}您好，我核對了 7/25 的服事表：\n\n📅 7/25 - 您有被排到 領歌\n\n請記得提前準備喔！🎵"}
            ])

            # 最後加入使用者的實際問題
            messages.append({"role": "user", "content": user_message})

            # 呼叫 OpenAI API
            response = openai.ChatCompletion.create(
                model="gpt-5.4-mini",  # 可以根據需要替換為其他模型
                messages=messages,
                temperature=0.2
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
            service_names = set(user_info["service_names"])
            for service_entry in context_data["services"]:
                relevant_services = []
                for service in service_entry["services"]:
                    # 將服事人員欄位依分隔符號拆開，逐一精確比對
                    import re
                    persons_in_cell = set(
                        re.split(r'[.、,，/]', service["person"]))
                    # 去除空白
                    persons_in_cell = {p.strip()
                                       for p in persons_in_cell if p.strip()}
                    # 精確比對：使用者名稱必須完全匹配其中一個人名
                    if service_names & persons_in_cell:
                        relevant_services.append(service)

                if relevant_services:
                    result["services"].append({
                        "date": service_entry["date"],
                        "services": relevant_services
                    })

        return result

    def _get_service_type_description(self):
        """取得服事類型說明"""
        from example.conf import field_code_conf
        descriptions = []
        for code, name in sorted(field_code_conf.items()):
            descriptions.append(f"- {name}")
        return "\n".join(descriptions)

    def _format_user_context(self, user_data, user_name):
        """格式化個人專屬資料為易讀格式"""
        if not user_data or not user_data.get("services"):
            return f"{user_name} 目前沒有排定的服事。"

        formatted = f"📋 {user_name} 的服事排程:\n\n"

        # 依日期排序
        services_by_date = sorted(
            user_data["services"], key=lambda x: x["date"])

        for service_entry in services_by_date:
            date = service_entry["date"]
            services = service_entry["services"]
            service_names = [s["type"] for s in services]
            formatted += f"📅 {date} - {' / '.join(service_names)}\n"

        return formatted.strip()

    def _format_all_services(self, services_data):
        """格式化完整服事表為結構化文字，使用表格式呈現方便 GPT 精確查找"""
        if not services_data:
            return "目前沒有服事資料。"

        formatted = "完整服事表（每一列代表一個日期，每個欄位列出負責人員）:\n\n"

        # 依日期排序
        services_sorted = sorted(services_data, key=lambda x: x["date"])

        for service_entry in services_sorted:
            date = service_entry["date"]
            formatted += f"【{date}】"

            # 按服事類型列出，用 | 分隔方便辨識
            parts = []
            for service in service_entry["services"]:
                parts.append(f"{service['type']}:{service['person']}")
            formatted += " | ".join(parts)
            formatted += "\n"

        return formatted.strip()
