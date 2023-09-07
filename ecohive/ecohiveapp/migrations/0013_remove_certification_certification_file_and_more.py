# Generated by Django 4.2.4 on 2023-09-05 04:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ecohiveapp', '0012_remove_category_category_image_product_product_image'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='certification',
            name='certification_file',
        ),
        migrations.AddField(
            model_name='certification',
            name='certification_image',
            field=models.ImageField(blank=True, null=True, upload_to='certification_image/'),
        ),
    ]
