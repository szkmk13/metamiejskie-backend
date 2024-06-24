# Generated by Django 4.2.13 on 2024-06-24 15:13

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Attendance",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("drinking", models.BooleanField(default=True)),
                ("confirmed", models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name="Meeting",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("date", models.DateField()),
                ("place", models.CharField(max_length=30)),
                ("other_place", models.CharField(blank=True, max_length=30, null=True)),
                ("pizza", models.BooleanField(default=False)),
                ("kasyno", models.BooleanField(default=False)),
                ("participants", models.ManyToManyField(through="meetings.Attendance", to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name="attendance",
            name="meeting",
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="meetings.meeting"),
        ),
        migrations.AddField(
            model_name="attendance",
            name="user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, related_name="+", to=settings.AUTH_USER_MODEL
            ),
        ),
    ]