from django.conf import settings
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.http import HttpResponse

from bot.views import telegram_webhook

def home(request):
    return HttpResponse("hello world")

urlpatterns = [
    path('', home),
    path("admin/", admin.site.urls),
    path("exam/", include("exam.urls")),   # 👈 add this
    path('webhook/', telegram_webhook, name='telegram_webhook')
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)