# Generated by Django 4.2.4 on 2023-09-17 02:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0026_seller_email_seller_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='productsummary',
            name='product_price',
            field=models.DecimalField(decimal_places=2, max_digits=10),
        ),
    ]