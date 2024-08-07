# Generated by Django 4.2.13 on 2024-07-03 13:29

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
            name="Game",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(default="", max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name="Symbol",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=128)),
                ("image", models.ImageField(upload_to="")),
                (
                    "weight",
                    models.PositiveIntegerField(
                        default=1,
                        help_text="Weight of the symbol, the higher number the bigger chance of it rolling",
                    ),
                ),
                (
                    "value",
                    models.PositiveIntegerField(
                        default=1,
                        help_text="Value of the symbol, if user rolls a line of them, this is the amount it'sgona be multiplied by",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Spin",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("time", models.DateTimeField(auto_now_add=True)),
                ("has_won", models.BooleanField(default=False)),
                ("chosen_lines", models.PositiveIntegerField(default=1)),
                (
                    "amount",
                    models.IntegerField(
                        validators=[django.core.validators.MinValueValidator(1)]
                    ),
                ),
                (
                    "game",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="casino.game"
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="game",
            name="symbols",
            field=models.ManyToManyField(
                blank=True, related_name="games", to="casino.symbol"
            ),
        ),
        migrations.CreateModel(
            name="HighCard",
            fields=[
                (
                    "game_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="casino.game",
                    ),
                ),
                ("last_card", models.CharField(default="", max_length=20)),
                (
                    "user",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            bases=("casino.game",),
        ),
    ]
