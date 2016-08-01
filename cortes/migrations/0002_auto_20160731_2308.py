# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cortes', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Export',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('week_number', models.SmallIntegerField()),
                ('file_id', models.CharField(max_length=200)),
                ('file_path', models.CharField(max_length=200)),
                ('usd_value', models.SmallIntegerField()),
                ('export_date', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.RemoveField(
            model_name='service',
            name='folio',
        ),
        migrations.AddField(
            model_name='booking',
            name='folio',
            field=models.SmallIntegerField(null=True, blank=True),
        ),
    ]
