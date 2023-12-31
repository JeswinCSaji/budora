# Generated by Django 4.2.4 on 2023-09-15 15:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0021_alter_certification_is_approved'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProductSummary',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('product_name', models.CharField(max_length=100, unique=True)),
                ('total_stock', models.IntegerField(default=0)),
                ('product_image', models.ImageField(blank=True, null=True, upload_to='product_images/')),
                ('product_description', models.TextField(blank=True, null=True)),
                ('product_price', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
            ],
        ),
        migrations.AddField(
            model_name='product',
            name='product_stock',
            field=models.IntegerField(default=0),
        ),
    ]
