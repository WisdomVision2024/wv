# Generated by Django 4.2.13 on 2024-06-05 10:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0010_rename_identity_userdata_identity_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userdata',
            name='Password',
            field=models.CharField(max_length=50),
        ),
    ]
