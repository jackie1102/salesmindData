import django
import os
import threading
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "salesmindData.settings")
django.setup()
lock = threading.Lock()