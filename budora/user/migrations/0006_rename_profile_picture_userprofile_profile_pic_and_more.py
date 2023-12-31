# Generated by Django 4.2.4 on 2023-09-03 05:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0005_delete_tbl_users'),
    ]

    operations = [
        migrations.RenameField(
            model_name='userprofile',
            old_name='profile_picture',
            new_name='profile_pic',
        ),
        migrations.RemoveField(
            model_name='userprofile',
            name='date_of_birth',
        ),
        migrations.AddField(
            model_name='userprofile',
            name='name',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.DeleteModel(
            name='Profile',
        ),
    ]
