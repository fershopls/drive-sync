# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Booking',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('book_nr', models.IntegerField()),
                ('book_date', models.DateTimeField()),
                ('booker_name', models.CharField(max_length=200)),
                ('guest_names', models.CharField(max_length=200)),
                ('arrival', models.DateField()),
                ('departure', models.DateField()),
                ('status', models.CharField(max_length=200)),
                ('total', models.SmallIntegerField()),
                ('commission', models.FloatField(default=0)),
                ('internal_notes', models.TextField(blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Concept',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='Currency',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('slug', models.CharField(max_length=10)),
            ],
        ),
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('value', models.IntegerField()),
                ('booking', models.ForeignKey(to='cortes.Booking')),
                ('currency', models.ForeignKey(to='cortes.Currency')),
            ],
        ),
        migrations.CreateModel(
            name='Service',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('folio', models.SmallIntegerField()),
                ('value', models.SmallIntegerField()),
                ('booking', models.ForeignKey(to='cortes.Booking')),
                ('concept', models.ForeignKey(to='cortes.Concept')),
                ('currency', models.ForeignKey(to='cortes.Currency')),
            ],
        ),
    ]
