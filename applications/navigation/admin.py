from django.contrib import admin

# Register your models here.
from .models import ModelType, Navigations, SortInfo, UserFaviourt

admin.site.register(ModelType)
admin.site.register(Navigations)
admin.site.register(SortInfo)
admin.site.register(UserFaviourt)
