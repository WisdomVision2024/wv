# Generated by Django 4.2.13 on 2024-06-02 10:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0006_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userdata',
            name='Email',
            field=models.TextField(),
        ),
        migrations.AlterField(
            model_name='userdata',
            name='Name',
            field=models.TextField(),
        ),
        migrations.AlterField(
            model_name='userdata',
            name='Phone',
            field=models.TextField(),
        ),
        migrations.AlterField(
            model_name='userdata',
            name='identity',
            field=models.TextField(),
        ),
    ]
