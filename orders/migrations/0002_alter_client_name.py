# Generated by Django 4.2.16 on 2024-12-04 04:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("orders", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="client",
            name="name",
            field=models.CharField(max_length=128, unique=True),
        ),
    ]