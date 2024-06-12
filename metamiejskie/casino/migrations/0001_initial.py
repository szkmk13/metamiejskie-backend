# Generated by Django 4.2.13 on 2024-06-07 12:59

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Game',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('lines', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Spin',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('time', models.DateTimeField(auto_now_add=True)),
                ('won', models.BooleanField(default=False)),
                ('amount', models.DecimalField(decimal_places=2, default=10, max_digits=5, validators=[django.core.validators.MinValueValidator(10)])),
                ('game', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='casino.game')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
