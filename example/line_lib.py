from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden

from linebot import LineBotApi, WebhookParser
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import MessageEvent, TextSendMessage
from django.conf import settings

class lineLib:
    def __init__(self):
        self.lines = []
        self.line_bot_api = LineBotApi(settings.LINE_CHANNEL_ACCESS_TOKEN)
        self.parser = WebhookParser(settings.LINE_CHANNEL_SECRET)

    def sendMessage(self,uuid,msg):

        self.line_bot_api.push_message(uuid, TextSendMessage(text=msg))

    def parseRequest(self,request):
        signature = request.META['HTTP_X_LINE_SIGNATURE']
        body = request.body.decode('utf-8')
        data = {}
        try:
            events = self.parser.parse(body, signature)
            event = events[0]
            user_id = event.source.user_id
            msg_type = event.source.type
            reply_token = event.reply_token

            profile = self.line_bot_api.get_profile(user_id)
            #url decode

            message = ''
            if isinstance(event, MessageEvent):
                message=event.message.text

            # message.append(TextSendMessage(text=mtext))
            # self.line_bot_api.reply_message(event.reply_token,message)

            data={
                'user_id':user_id,
                # 'profile':profile,
                'user_name':profile.display_name,
                'message':message,
                'msg_type':msg_type,
                'reply_token':reply_token
            }
            return data
        except InvalidSignatureError:
            return HttpResponseForbidden()
        except LineBotApiError:
            return HttpResponseBadRequest()


