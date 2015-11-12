# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0002_auto_20151111_0012'),
    ]

    operations = [
        migrations.RenameField(
            model_name='userprofile',
            old_name='ccn_exp',
            new_name='ccnexp',
        ),
        migrations.AddField(
            model_name='userprofile',
            name='address2',
            field=models.CharField(max_length=100, default=''),
            preserve_default=False,
        ),
    ]
