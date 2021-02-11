from django.conf.urls import url
from .views import runjob

urlpatterns = [
    url(r'cron', runjob),
]