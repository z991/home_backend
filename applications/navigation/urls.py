from django.conf.urls import url, include
from rest_framework import routers
from rest_framework.urlpatterns import format_suffix_patterns

from . import views

router = routers.DefaultRouter()
router.register(r'type', views.TypeViewSet)

urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'get_myfavourite', views.get_myfavourite, name='get_myfavourite'),
    url(r'post_myfavourite', views.post_myfavourite, name='post_myfavourite'),
    url(r'delete_myfavourite', views.delete_myfaourite, name='delete_myfaourite'),
    url(r'set_sort', views.set_sort, name='set_sort'),

]

api_urls = router.urls + urlpatterns