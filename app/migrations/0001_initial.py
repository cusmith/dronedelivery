# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Drone',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('status', models.CharField(max_length=20, choices=[(b'idle', b'Idle'), (b'delivering', b'Delivering'), (b'returning', b'Returning'), (b'maintenance', b'Maintenance')])),
                ('location', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='InventoryType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('product_name', models.CharField(max_length=50)),
                ('stock_count', models.IntegerField(default=0)),
                ('description', models.CharField(max_length=200)),
                ('price', models.DecimalField(max_digits=8, decimal_places=2)),
            ],
        ),
        migrations.CreateModel(
            name='Invoice',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('status', models.CharField(max_length=20, choices=[(b'pending', b'Pending'), (b'delivering', b'Delivering'), (b'complete', b'Complete')])),
            ],
        ),
        migrations.CreateModel(
            name='InvoiceItem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('drone', models.ForeignKey(to='app.Drone')),
                ('inventory_type', models.ForeignKey(to='app.InventoryType')),
                ('invoice', models.ForeignKey(to='app.Invoice')),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('username', models.CharField(max_length=50)),
                ('name', models.CharField(max_length=50)),
                ('address', models.CharField(max_length=100)),
                ('email', models.CharField(max_length=50)),
                ('phone_number', models.CharField(max_length=10)),
            ],
        ),
        migrations.AddField(
            model_name='invoice',
            name='user',
            field=models.ForeignKey(to='app.User'),
        ),
    ]
