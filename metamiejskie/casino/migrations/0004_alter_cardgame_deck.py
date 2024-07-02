# Generated by Django 4.2.13 on 2024-07-01 20:02

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("casino", "0003_cardgame"),
    ]

    operations = [
        migrations.AlterField(
            model_name="cardgame",
            name="deck",
            field=models.JSONField(
                default=[
                    (2, "clubs"),
                    (2, "hearts"),
                    (2, "diamonds"),
                    (2, "spades"),
                    (3, "clubs"),
                    (3, "hearts"),
                    (3, "diamonds"),
                    (3, "spades"),
                    (4, "clubs"),
                    (4, "hearts"),
                    (4, "diamonds"),
                    (4, "spades"),
                    (5, "clubs"),
                    (5, "hearts"),
                    (5, "diamonds"),
                    (5, "spades"),
                    (6, "clubs"),
                    (6, "hearts"),
                    (6, "diamonds"),
                    (6, "spades"),
                    (7, "clubs"),
                    (7, "hearts"),
                    (7, "diamonds"),
                    (7, "spades"),
                    (8, "clubs"),
                    (8, "hearts"),
                    (8, "diamonds"),
                    (8, "spades"),
                    (9, "clubs"),
                    (9, "hearts"),
                    (9, "diamonds"),
                    (9, "spades"),
                    (10, "clubs"),
                    (10, "hearts"),
                    (10, "diamonds"),
                    (10, "spades"),
                    ("jack", "clubs"),
                    ("jack", "hearts"),
                    ("jack", "diamonds"),
                    ("jack", "spades"),
                    ("queen", "clubs"),
                    ("queen", "hearts"),
                    ("queen", "diamonds"),
                    ("queen", "spades"),
                    ("king", "clubs"),
                    ("king", "hearts"),
                    ("king", "diamonds"),
                    ("king", "spades"),
                    ("ace", "clubs"),
                    ("ace", "hearts"),
                    ("ace", "diamonds"),
                    ("ace", "spades"),
                ]
            ),
        ),
    ]
