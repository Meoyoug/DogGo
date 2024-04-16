# Generated by Django 5.0.4 on 2024-04-09 07:13

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("categories", "0001_initial"),
        ("products", "0002_product_product_img_alter_product_sale"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="category",
            name="product",
        ),
        migrations.CreateModel(
            name="CategoryProductConnector",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("modified_at", models.DateTimeField(auto_now=True)),
                ("category", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="categories.category")),
                ("product", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="products.product")),
            ],
            options={
                "abstract": False,
            },
        ),
    ]
