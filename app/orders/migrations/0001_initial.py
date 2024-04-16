# Generated by Django 5.0.4 on 2024-04-15 09:36

import uuid

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("coupons", "0001_initial"),
        ("products", "0002_alter_product_description_img_and_more"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Order",
            fields=[
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("modified_at", models.DateTimeField(auto_now=True)),
                (
                    "order_id",
                    models.UUIDField(
                        default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True
                    ),
                ),
                ("sale_price", models.IntegerField(default=0)),
                ("total_price", models.IntegerField()),
                (
                    "status",
                    models.CharField(
                        choices=[("CANCEL", "cancel"), ("PAID", "paid"), ("ORDERED", "ordered")],
                        default="ordered",
                        max_length=7,
                    ),
                ),
                ("people", models.IntegerField(default=0)),
                ("pet", models.IntegerField(default=0)),
                ("pet_size_big", models.IntegerField(default=0)),
                ("pet_size_medium", models.IntegerField(default=0)),
                ("pet_size_small", models.IntegerField(default=0)),
                ("departure_date", models.DateField(default=None)),
                ("return_date", models.DateField(default=None)),
                (
                    "product",
                    models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to="products.product"),
                ),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                (
                    "user_coupon",
                    models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to="coupons.usercoupon"),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="Payment",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("modified_at", models.DateTimeField(auto_now=True)),
                (
                    "payment_method",
                    models.CharField(
                        choices=[
                            ("credit_card", "신용카드"),
                            ("bank_transfer", "무통장 입금"),
                            ("toss_pay", "토스페이"),
                        ],
                        max_length=20,
                    ),
                ),
                ("amount", models.PositiveIntegerField(default=0)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("PENDING", "pending"),
                            ("SUCCESS", "success"),
                            ("FAILED", "failed"),
                            ("CANCELLED", "cancelled"),
                            ("REFUNDED", "refunded"),
                        ],
                        max_length=10,
                    ),
                ),
                ("order", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="orders.order")),
            ],
            options={
                "abstract": False,
            },
        ),
    ]
