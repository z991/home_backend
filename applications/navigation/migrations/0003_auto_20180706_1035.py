# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-07-06 10:35
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('navigation', '0002_auto_20180706_1030'),
    ]

    operations = [
        migrations.AlterField(
            model_name='navigations',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='', verbose_name='图片'),
        ),
    ]