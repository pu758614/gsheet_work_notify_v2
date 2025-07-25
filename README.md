# 服事提醒小天使 (gsheet_work_notify_v2)

這是一個基於 LINE Bot 的教會服事提醒系統，可以根據 Google Sheet 中的服事資料自動發送提醒訊息。

## 功能

1. **自動提醒服事**：根據設定的提醒日，提醒使用者本週的服事
2. **查詢服事**：使用者可以查詢自己接下來的服事
3. **設定提醒日**：使用者可以自行設定在每週的哪一天提醒
4. **AI 自然語言互動**：使用者可以用自然語言向系統提問，系統會使用 GPT 進行回答

## 快速開始

### Docker 方式

```bash
# 建立 Docker 映像
docker build . -t gsheet_work_notify_v2

# 執行容器
docker run -p 5000:5000 -v .:/code gsheet_work_notify_v2
```

### 定時任務設定

定時提醒功能使用 cron job 實現，可以在以下網站設定：
https://console.cron-job.org/

## 新功能：GPT 自然語言互動

現在使用者可以透過自然語言與小天使互動。只需發送以「小天使, 」開頭的訊息，系統會將使用者的問題和 Google Sheet 中的服事資料提供給 GPT，生成智能回答。

詳細說明請參閱 [GPT_FEATURE_README.md](GPT_FEATURE_README.md)