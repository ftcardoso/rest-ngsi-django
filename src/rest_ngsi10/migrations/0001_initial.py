# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import jsonfield.fields
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('doh', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='HookRelation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('hook', models.OneToOneField(to='doh.Hook')),
            ],
        ),
        migrations.CreateModel(
            name='Subscription',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('attributes', jsonfield.fields.JSONField(null=True, blank=True)),
                ('conditions', jsonfield.fields.JSONField(null=True, blank=True)),
                ('hooks', models.ManyToManyField(to='doh.Hook', through='rest_ngsi10.HookRelation')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='hookrelation',
            name='subscription',
            field=models.ForeignKey(to='rest_ngsi10.Subscription'),
        ),
    ]
