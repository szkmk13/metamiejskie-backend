# Generated by Django 4.2.13 on 2024-06-26 14:58

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("meetings", "0002_place_rename_kasyno_meeting_casino_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="meeting",
            name="confirmed_by_majority",
            field=models.BooleanField(default=False),
        ),
    ]