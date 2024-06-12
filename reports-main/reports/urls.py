from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.urls import path, reverse_lazy

urlpatterns = [
    path('Paramotor-admin/', admin.site.urls),
    path('', include('merchant.urls')),
    path('upload/', include('upload_report.urls')),
    path('send-reports/', include('send_report.urls')),
    path('accounts/', include('django.contrib.auth.urls'), name='auth'),
    #

    # Redirect Logout
    path('logout/', auth_views.LogoutView.as_view(
         next_page=reverse_lazy('login')
         # you can use your named URL here just like you use the **url** tag in your django template
     ), name='logout'),
]

# urlpatterns for static file (CSS, JS, Images, Fonts ect.)
urlpatterns += staticfiles_urlpatterns()
