# Generated by Django 4.2.13 on 2024-07-07 14:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0012_alter_userdata_phone'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userdata',
            name='Identity',
            field=models.BooleanField(default=False),
        ),
    ]
