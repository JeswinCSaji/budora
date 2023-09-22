# Generated by Django 4.2.4 on 2023-09-18 15:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0029_productsummary_humidity_requirements_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='productsummary',
            name='product_sci_name',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='productsummary',
            name='total_stock',
            field=models.IntegerField(blank=True, default=0, null=True),
        ),
    ]