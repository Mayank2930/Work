from django.urls import path
from .views import *

urlpatterns = [
    path('check-merchant/send-reports/', send_reports_and_log_mail , name='send_reports'),
    path('check-merchant/', check_merchant, name='check_merchant'),
]
