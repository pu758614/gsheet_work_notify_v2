# example/views.py
from datetime import datetime
from django.http import HttpResponse
from rest_framework.decorators import api_view
from django.conf import settings
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden

from linebot import LineBotApi, WebhookParser
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import MessageEvent, TextSendMessage
from example.line_lib import lineLib
from example.sheet_lib import googleSheet
from example.gpt_lib import GptLib
from example import daily_notify_lib
from icalendar import Calendar, Event
from django.utils import timezone
import time


@api_view(["GET"])
def trigger_notify(request):
    daily_notify_lib.daily_notify()
    return HttpResponse('123456')


@api_view(["POST"])
def lineCallback(request):
    line_lib = lineLib()
    data = line_lib.parseRequest(request)
    if (len(data) == 0):
        return HttpResponse()
    google_sheet_lib = googleSheet('user')
    check_result = google_sheet_lib.check_user(data['user_id'])
    send_msg_list = []
    if (check_result == False):
        google_sheet_lib.add_user(data['user_id'], data['user_name'])
        send_msg_list.append(
            f"{data['user_name']} ~ 平安！ 我是您的服事提醒小天使，我會每週提醒您當週的服事！\n但請注意，有時候我的資訊會錯誤或是睡過頭忘記了{line_lib.emoji('100095')}，\n所以還是請您以教會週報、群組服事表為主呦！\n\n請待管理員協助設定帳號，設定完成後才會有正常的通知喔！{line_lib.emoji('10008D')}")
        line_lib.replySendMessage(data['reply_token'], send_msg_list)
        return HttpResponse()

    user_info = google_sheet_lib.get_user_info(data['user_id'])

    msg = data['message']

    set_conf = {
        '小天使, 請禮拜一提醒我': 1,
        '小天使, 請禮拜二提醒我': 2,
        '小天使, 請禮拜三提醒我': 3,
        '小天使, 請禮拜四提醒我': 4,
        '小天使, 請禮拜五提醒我': 5,
        '小天使, 請禮拜六提醒我': 6,
        '小天使, 請禮拜日提醒我': 7,
        '小天使, 請先不用提醒我': 0,
    }

    day_conf = {
        1: '一',
        2: '二',
        3: '三',
        4: '四',
        5: '五',
        6: '六',
        7: '日',
    }
    send_msg = ''
    log_type = 'echo'
    if (msg in set_conf):
        notify_day = set_conf[msg]
        google_sheet_lib.set_user_notify_day(data['user_id'], notify_day)
        if (notify_day != 0):
            send_msg = f"收到！會在每週{day_conf[notify_day]}提醒您的！"
        else:
            send_msg = f"收到！已取消提醒！"
        # line_lib.replySendMessage(data['reply_token'],[send_msg])
    elif (msg == '小天使, 請問我接下來服事有哪些?'):

        now_year = datetime.now().strftime('%Y')
        user_work_name_list = googleSheet('user').getWorkNames(data['user_id'])

        work_list = googleSheet(now_year).getNextWorks(user_work_name_list)
        if (work_list != {}):
            send_msg = '您接下來的服事有：\n'
            for work_date in work_list:
                work_name_list = work_list[work_date]
                work_name_str = '、'.join(work_name_list)
                send_msg += f"{work_date} {work_name_str}\n"
            send_msg += "\n請您預備心服事呦。"+line_lib.emoji("10008D")
        else:
            send_msg = f'您接下來暫時沒有其他服事呦！'+line_lib.emoji("10008E")
    elif (msg == '小天使, 我要把接下來的服事加入行事曆！'):
        # 這裡可以加入生成並回傳 .ics 檔案的邏輯
        send_msg = "以下連結可以下載您的服事行事曆檔案，打開後可以幫你把服事匯進您的行事曆喔！請點擊連結下載：\n http://gsheet-work-notify-v2.vercel.app/export_ics?user_id=" + \
            data['user_id']
    elif (msg == '小天使, 請問這怎麼用?'):
        notify_user_name = data['user_name']
        send_msg = f"嗨 {notify_user_name} ~ 您可以點選下方選單日~六設定通知日，若不想接收通知請點選「關閉提醒」。\n\n"
        if (user_info['notify_day'] == 0):
            send_msg += f"目前您已經關閉提醒囉！"
        else:
            send_msg += f"目前您的通知日是星期{day_conf[user_info['notify_day']]}喔！"
    # 處理自然語言查詢 - 如果訊息以「小天使」開頭但不是上述預設命令，則視為 GPT 查詢
    else:
        # 創建 GPT 庫實例
        gpt_lib = GptLib()

        # 獲取 GPT 回應
        gpt_response = gpt_lib.query_gpt(
            msg,
            user_id=data['user_id'],
            user_name=data['user_name']
        )

        send_msg = gpt_response
        # AI警語
        send_msg += "\n\n提醒：以上內容由AI回覆，僅供參考，請自行判斷其正確性。"
        log_type = 'echo_gpt'

    if (send_msg != ''):
        send_msg_list.append(send_msg)
    if (len(send_msg_list) > 0):
        line_lib.replySendMessage(data['reply_token'], send_msg_list)
    googleSheet('record').write_record(
        data['user_name'], log_type, msg, send_msg)
    return HttpResponse()


@api_view(["GET"])
def export_ics(request):
    """
    匯出使用者的服事行事曆 .ics 檔案
    參數: user_id (從 query parameter 取得)
    """
    user_id = request.GET.get('user_id', None)

    if not user_id:
        return HttpResponseBadRequest('缺少 user_id 參數')

    # 檢查使用者是否存在
    google_sheet_lib = googleSheet('user')
    if not google_sheet_lib.check_user(user_id):
        return HttpResponseBadRequest('找不到此使用者')

    # 取得使用者資訊
    user_info = google_sheet_lib.get_user_info(user_id)
    user_name = user_info.get('user_name', '使用者')

    # 取得使用者的服事名稱列表
    user_work_name_list = google_sheet_lib.getWorkNames(user_id)

    # 取得今年的服事列表
    now_year = datetime.now().strftime('%Y')
    work_list = googleSheet(now_year).getNextWorks(user_work_name_list)

    # 建立 iCalendar
    cal = Calendar()
    cal.add('prodid', '-//教會服事提醒//mxm.dk//')
    cal.add('version', '2.0')
    cal.add('x-wr-calname', f'{user_name} 的服事行事曆')
    cal.add('x-wr-timezone', 'Asia/Taipei')

    # 為每個服事建立事件
    for work_date_str, work_names in work_list.items():
        # 將日期字串轉換為完整日期 (加上年份)
        full_date_str = f"{now_year}/{work_date_str}"
        work_date = datetime.strptime(full_date_str, '%Y/%m/%d')

        # 設定時間為下午 5 點到 6 點
        start_time = work_date.replace(hour=17, minute=0, second=0)
        end_time = work_date.replace(hour=18, minute=0, second=0)

        # 將同一天的所有服事合併成一個事件
        work_names_str = '、'.join(work_names)
        event = Event()
        event.add('summary', f'服事：{work_names_str}')
        event.add('dtstart', start_time)
        event.add('dtend', end_time)
        event.add('dtstamp', datetime.now())
        event.add('description',
                  f'{user_name} 在 {work_date_str} 的服事項目：{work_names_str}')
        event.add('location', '三民聖教會')
        event.add('status', 'CONFIRMED')

        # 設定提醒 (前一天提醒)
        # alarm = Alarm()
        # alarm.add('action', 'DISPLAY')
        # alarm.add('trigger', timedelta(days=-1))
        # alarm.add('description', f'明天有服事：{work_names_str}')
        # event.add_component(alarm)

        cal.add_component(event)

    # 產生 .ics 檔案內容
    ics_content = cal.to_ical()

    # 設定 HTTP 回應
    response = HttpResponse(
        ics_content, content_type='text/calendar; charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename="{user_name}_service_calendar.ics"'

    return response


def index(request):
    now = datetime.now()
    msg = daily_notify_lib.daily_notify_test()
    html = f'''
    <html>
        <body>
            <h1>19191988888888Hello from Vercel!</h1>
            <p>The current time is { now }.</p>
        </body>
        {msg}
    </html>
    '''
    time.sleep(15)

    return HttpResponse(html,)
    # return HttpResponse(html)
