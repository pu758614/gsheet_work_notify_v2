# example/views.py
from datetime import datetime
from django.http import HttpResponse
from rest_framework.decorators import api_view
from linebot.v3 import (
    WebhookHandler
)

@api_view(["POST"])
def lineCallback(request):
    handler = WebhookHandler('106f2024befbdc5e77609812307eee3b')
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    handler.handle(body, signature)

    # handle webhook body


    return 'OK'



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