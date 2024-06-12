from django.urls import path
from .views import *

urlpatterns = [
    path('', upload_files, name='upload_files'),
    path('download/', download, name='download'),
]
