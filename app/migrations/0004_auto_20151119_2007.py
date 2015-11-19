# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0003_auto_20151111_0723'),
    ]

    operations = [
        migrations.AlterField(
            model_name='invoiceitem',
            name='drone',
            field=models.ForeignKey(to='app.Drone', null=True),
        ),
    ]
