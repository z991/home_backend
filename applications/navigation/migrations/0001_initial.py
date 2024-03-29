# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-07-06 09:53
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ModelType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now=True, help_text='创建时间')),
                ('updated_at', models.DateTimeField(auto_now_add=True, help_text='更新时间')),
                ('name_type', models.CharField(max_length=128, verbose_name='分类名字')),
            ],
            options={
                'verbose_name': '导航分类',
                'verbose_name_plural': '导航分类',
                'permissions': (('view_type', 'Can see available type'),),
            },
        ),
        migrations.CreateModel(
            name='Navigations',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now=True, help_text='创建时间')),
                ('updated_at', models.DateTimeField(auto_now_add=True, help_text='更新时间')),
                ('name_navigations', models.CharField(max_length=128, verbose_name='导航名称')),
                ('url', models.URLField(blank=True, null=True, verbose_name='导航链接')),
                ('desc', models.CharField(blank=True, max_length=128, null=True, verbose_name='描述')),
                ('image', models.URLField(blank=True, null=True, verbose_name='图片')),
                ('type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='navigations_of', to='navigation.ModelType', verbose_name='导航分类')),
            ],
            options={
                'verbose_name': '导航名称',
                'verbose_name_plural': '导航名称',
                'permissions': (('view_navigations', 'Can see available navigations'),),
            },
        ),
        migrations.CreateModel(
            name='SortInfo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now=True, help_text='创建时间')),
                ('updated_at', models.DateTimeField(auto_now_add=True, help_text='更新时间')),
                ('order', models.TextField(verbose_name='排序规则')),
                ('username', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='用户排序')),
            ],
            options={
                'verbose_name': '排序信息',
                'verbose_name_plural': '排序信息',
                'permissions': (('view_sortinfo', 'Can see available sortinfo'),),
            },
        ),
        migrations.CreateModel(
            name='UserFaviourt',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now=True, help_text='创建时间')),
                ('updated_at', models.DateTimeField(auto_now_add=True, help_text='更新时间')),
                ('faviourt', models.ManyToManyField(related_name='navigation_fav', to='navigation.Navigations', verbose_name='导航名字')),
                ('user_faviourt', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='用户收藏')),
            ],
            options={
                'verbose_name': '我的收藏',
                'verbose_name_plural': '我的收藏',
                'permissions': (('view_userfaviourt', 'Can see available userfaviourt'),),
            },
        ),
    ]
