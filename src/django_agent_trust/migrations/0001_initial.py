# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='AgentSettings',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('trust_days', models.FloatField(default=None, help_text='The number of days a agent will remain trusted.', null=True, blank=True)),
                ('inactivity_days', models.FloatField(default=None, help_text="The number of days allowed between requests before a agent's trust is revoked.", null=True, blank=True)),
                ('serial', models.IntegerField(default=0, help_text='Increment this to revoke all previously trusted agents.')),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)),
            ],
        ),
    ]
