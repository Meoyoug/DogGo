# Generated by Django 5.0.4 on 2024-04-16 13:17

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("products", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="ProductReview",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("modified_at", models.DateTimeField(auto_now=True)),
                ("title", models.CharField(max_length=50)),
                ("content", models.TextField(max_length=500)),
                ("image_url", models.URLField(blank=True, null=True)),
                ("status", models.BooleanField(default=True)),
                (
                    "product",
                    models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to="products.product"),
                ),
                (
                    "user",
                    models.ForeignKey(
                        null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
    ]
