from django.urls import path
from .views import *

urlpatterns = [
    path('', home, name='home'),
    path('merchant-form/', merchant_form, name='merchant_form'),
    path('merchant-form/merchant-bulk-upload/', merchant_bulk_upload, name='merchant_bulk_upload'),
    path('merchant-detail/<id>/', merchant_detail, name='merchant_detail_page'),
    path('merchant-detail/<id>/delete', delete_merchant, name='delete_merchant'),
]
