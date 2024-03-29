# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-07-06 10:30
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('navigation', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='modeltype',
            name='name_type',
            field=models.CharField(max_length=128, unique=True, verbose_name='分类名字'),
        ),
        migrations.AlterField(
            model_name='navigations',
            name='name_navigations',
            field=models.CharField(max_length=128, unique=True, verbose_name='导航名称'),
        ),
        migrations.AlterUniqueTogether(
            name='navigations',
            unique_together=set([('name_navigations', 'type')]),
        ),
    ]
