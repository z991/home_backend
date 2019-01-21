"""home_backend URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from django.conf import settings
#处理媒体文件的API
from django.views.static import serve
from django import views

api_urls = [
    url('^backend/', include('applications.backend.urls')),
    url('^navigation/', include('applications.navigation.urls')),
    url('^account/', include('applications.user_manage.urls')),
    url('^log/', include('applications.log_manage.urls')),
]


urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url('^api/', include(api_urls)),
    # 写一个媒体文件的url，并且用serve函数处理，指定媒体文件的路径
    url(r'^upload/(.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
]
