# Generated by Django 5.0.4 on 2024-04-09 13:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("coupons", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="usercoupon",
            name="status",
            field=models.BooleanField(default=True),
        ),
    ]
