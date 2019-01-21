from django.conf.urls import url
from rest_framework import routers
# from rest_framework_jwt.views import obtain_jwt_token

from applications.backend import views
from applications.backend import viewsUtil

router = routers.DefaultRouter()


api_urls = router.urls + [
]

urlpatterns = [
    url(r'^login/$', views.login),
    url(r'^logout/$', views.logout),
    url(r'^verifycode/$', viewsUtil.verifycode),
    url(r'^permission/$', views.account_permission)
]