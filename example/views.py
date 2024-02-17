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
  # get X-Line-Signature header value
    # handler = WebhookHandler('106f2024befbdc5e77609812307eee3b')
    signature = request.META['HTTP_X_LINE_SIGNATURE']
    body = request.body.decode('utf-8')
    line_lib = lineLib()
    data = line_lib.parseRequest(request)
    if(len(data) == 0):
        return HttpResponse()
    google_sheet_lib = googleSheet('user')
    check_result = google_sheet_lib.check_user(data['user_id'])
    msg_list = []
    if(check_result == False):
        google_sheet_lib.add_user(data['user_id'],data['user_name'])
        msg_list.append(TextSendMessage(text='歡迎新朋友'))
    else:
        msg_list.append(TextSendMessage(text='歡迎回來'))
    # try:
    #     events = parser.parse(body, signature)
    # except InvalidSignatureError:
    #     return HttpResponseForbidden()
    # except LineBotApiError:
    #     return HttpResponseBadRequest()

    # for event in events:
    #     #class to json
    #     user_id = event.source.user_id
    #     # print(event.source.user_id)

    #     profile = line_bot_api.get_profile(user_id)

    #     print(profile)
    #     if isinstance(event, MessageEvent):
    #         mtext=event.message.text
    #         message=[]
    #         message.append(TextSendMessage(text=mtext))
    #         line_bot_api.reply_message(event.reply_token,message)

    return HttpResponse()





def index(request):
    now = datetime.now()
    html = f'''
    <html>
        <body>
            <h1>aaaaaaaaaHello from Vercel!</h1>
            <p>The current time is { now }.</p>
        </body>
    </html>
    '''
    return HttpResponse(html)