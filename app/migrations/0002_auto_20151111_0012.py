# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('app', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, verbose_name='ID', auto_created=True)),
                ('address1', models.CharField(max_length=100)),
                ('ccn', models.CharField(max_length=16)),
                ('ccn_exp', models.DateField()),
            ],
        ),
        migrations.AlterField(
            model_name='drone',
            name='status',
            field=models.CharField(max_length=20, choices=[('idle', 'Idle'), ('delivering', 'Delivering'), ('returning', 'Returning'), ('maintenance', 'Maintenance')]),
        ),
        migrations.AlterField(
            model_name='invoice',
            name='status',
            field=models.CharField(max_length=20, choices=[('pending', 'Pending'), ('delivering', 'Delivering'), ('complete', 'Complete')]),
        ),
        migrations.AlterField(
            model_name='invoice',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
        ),
        migrations.DeleteModel(
            name='User',
        ),
        migrations.AddField(
            model_name='userprofile',
            name='user',
            field=models.OneToOneField(to=settings.AUTH_USER_MODEL),
        ),
    ]
