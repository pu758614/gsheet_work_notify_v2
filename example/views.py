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
from example import daily_notify_lib

@api_view(["GET"])
def trigger_notify(request):
    daily_notify_lib.daily_notify()
    return HttpResponse('123456')


@api_view(["POST"])
def lineCallback(request):
    line_lib = lineLib()
    data = line_lib.parseRequest(request)
    if(len(data) == 0):
        return HttpResponse()
    google_sheet_lib = googleSheet('user')
    check_result = google_sheet_lib.check_user(data['user_id'])
    send_msg_list = []
    if(check_result == False):
        google_sheet_lib.add_user(data['user_id'],data['user_name'])
        send_msg_list.append(f"{data['user_name']} ~ 平安！ 我是您的服事提醒小天使，我會每週提醒您當週的服事！\n但請注意，有時候我的資訊會錯誤或是睡過頭忘記了{line_lib.emoji('100095')}，\n所以還是請您以教會週報、群組服事表為主呦！\n\n請待管理員協助設定帳號，設定完成後才會有正常的通知喔！{line_lib.emoji('10008D')}")
        line_lib.replySendMessage(data['reply_token'],send_msg_list)
        return HttpResponse()


    user_info = google_sheet_lib.get_user_info(data['user_id'])


    msg = data['message']

    set_conf = {
        '小天使, 請禮拜日提醒我': 1,
        '小天使, 請禮拜一提醒我': 2,
        '小天使, 請禮拜二提醒我': 3,
        '小天使, 請禮拜三提醒我': 4,
        '小天使, 請禮拜四提醒我': 5,
        '小天使, 請禮拜五提醒我': 6,
        '小天使, 請禮拜六提醒我': 7,
        '小天使, 請先不用提醒我': 0,
    }

    day_conf = {
        1: '日',
        2: '一',
        3: '二',
        4: '三',
        5: '四',
        6: '五',
        7: '六',
    }
    send_msg = ''
    if(msg in set_conf):
        notify_day = set_conf[msg]
        google_sheet_lib.set_user_notify_day(data['user_id'],notify_day)
        if(notify_day!=0):
            send_msg = f"收到！會在每週{day_conf[notify_day]}提醒您的！"
        else:
            send_msg = f"收到！已取消提醒！"
        # line_lib.replySendMessage(data['reply_token'],[send_msg])
    elif(msg=='小天使, 請問我接下來服事有哪些?'):

        now_year = datetime.now().strftime('%Y')
        user_work_name_list=googleSheet('user').getWorkNames(data['user_id'])

        work_list = googleSheet(now_year).getNextWorks(user_work_name_list)
        if(work_list!={}):
            send_msg = '您接下來的服事有：\n'
            for work_date in work_list:
                work_name_list = work_list[work_date]
                work_name_str = '、'.join(work_name_list)
                send_msg += f"{work_date} {work_name_str}\n"
            send_msg += "\n請您預備心服事呦。"+line_lib.emoji("10008D")
        else:
            send_msg = f'您接下來暫時沒有其他服事呦！'+line_lib.emoji("10008E")
    elif(msg=='小天使, 請問這怎麼用?'):
        notify_user_name = data['user_name']
        send_msg = f"嗨 {notify_user_name} ~ 您可以點選下方選單日~六設定通知日，若不想接收通知請點選「關閉提醒」。\n\n";
        if(user_info['notify_day']==0):
            send_msg += f"目前您已經關閉提醒囉！"
        else:
            send_msg += f"目前您的通知日是星期{day_conf[user_info['notify_day']]}喔！"

    if(send_msg!=''):
        send_msg_list.append(send_msg)
    if(len(send_msg_list)>0):
        line_lib.replySendMessage(data['reply_token'],send_msg_list)


    return HttpResponse()





def index(request):
    now = datetime.now()
    html = f'''
    <html>
        <body>
            <h1>yyyyyyHello from Vercel!</h1>
            <p>The current time is { now }.</p>
        </body>
    </html>
    '''
    return HttpResponse(html)