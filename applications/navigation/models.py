from django.db import models
from common.models import TimeStampModel
from django.contrib.auth.models import User


# Create your models here.
class ModelType(TimeStampModel):
    name_type = models.CharField(max_length=128, unique=True, verbose_name="分类名字")

    class Meta:
        permissions = (
            ("view_type", "Can see available type"),
        )
        verbose_name_plural = verbose_name = "导航分类"

    def __str__(self):
        return self.name_type


class Navigations(TimeStampModel):
    name_navigations = models.CharField(max_length=128, unique=True, verbose_name="导航名称")
    type = models.ForeignKey('ModelType', related_name="navigations_of", verbose_name="导航分类")
    url = models.URLField(verbose_name="导航链接", null=True, blank=True)
    desc = models.CharField(max_length=128, verbose_name="描述", null=True, blank=True)
    image = models.ImageField(verbose_name="图片", upload_to='avatar/', default='avatar/default.jpg')

    class Meta:
        unique_together = ('name_navigations', 'type')
        permissions = (
            ("view_navigations", "Can see available navigations"),
        )
        verbose_name_plural = verbose_name = "导航名称"

    def __str__(self):
        return self.name_navigations


class SortInfo(TimeStampModel):
    username = models.ForeignKey(User, verbose_name="用户排序")
    order = models.TextField(verbose_name="排序规则")

    class Meta:
        permissions = (
            ("view_sortinfo", "Can see available sortinfo"),
        )
        verbose_name_plural = verbose_name = "排序信息"

    def __str__(self):
        return str(self.username)


class UserFaviourt(TimeStampModel):
    user_faviourt = models.OneToOneField(User, verbose_name="用户收藏")
    faviourt = models.ManyToManyField('Navigations', related_name="navigation_fav", verbose_name="导航名字")

    class Meta:
        permissions = (
            ("view_userfaviourt", "Can see available userfaviourt"),
        )
        verbose_name_plural = verbose_name = "我的收藏"

    def __str__(self):
        return str(self.user_faviourt)