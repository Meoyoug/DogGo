# Generated by Django 5.0.4 on 2024-04-11 14:41

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("orders", "0004_remove_order_coupon_order_usercoupon_and_more"),
    ]

    operations = [
        migrations.RenameField(
            model_name="order",
            old_name="UserCoupon",
            new_name="user_coupon",
        ),
    ]
