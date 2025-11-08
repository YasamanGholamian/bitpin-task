from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse

def health(request):
    return HttpResponse("ok", status=200)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("healthz/", health), 
    path("", include('dashboard.urls')),
    path("", include('users.urls')),
    path("", include('trading.urls')),
]
