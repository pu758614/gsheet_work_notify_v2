import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE","api.settings")
django.setup()


from example import daily_notify_lib


daily_notify_lib.daily_notify()