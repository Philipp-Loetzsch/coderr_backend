# Generated by Django 5.2 on 2025-05-06 19:17

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('offers_app', '0004_rename_delivery_time_offerdetail_delivery_time_in_days'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='offerdetail',
            name='description',
        ),
    ]
