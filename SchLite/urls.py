"""SchLite URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.views.generic import TemplateView, RedirectView

from .settings import BASE_DIR
import auth.views
import wall.views
from django.urls import path, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse
from django.http import FileResponse, HttpRequest
from os.path import join as ojoin


def return_icon(request: HttpRequest):
    print(ojoin('./static/', 'icons/', request.path[1:].replace('..', '')))
    icon = open(ojoin('./static/', 'icons/', request.path[1:]), 'rb')
    response = FileResponse(icon, filename=request.path)
    return response



urlpatterns = [
    path('', wall.views.wall),
    path('login/', auth.views.login),
    path('logout/', auth.views.logout),
    path('api_schedule/', wall.views.api_schedule),
    path('api_offline_schedule/', wall.views.api_offline_schedule),
    path('api_get_done/', wall.views.api_get_done),
    path('api_set_done/', wall.views.api_set_done),
    path('api_get_backpack/', wall.views.api_today_backpack),
    re_path(r'^sw.js', wall.views.get_sw),
    re_path(r'.*icon.*', return_icon),
    # path('admin/', admin.site.urls),
] + static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS) \
  + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
