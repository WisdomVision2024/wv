# Generated by Django 4.2.13 on 2024-05-29 12:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0002_alter_user_email'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='Email',
            field=models.TextField(),
        ),
        migrations.AlterField(
            model_name='user',
            name='Name',
            field=models.TextField(),
        ),
        migrations.AlterField(
            model_name='user',
            name='Password',
            field=models.TextField(),
        ),
        migrations.AlterField(
            model_name='user',
            name='Phone',
            field=models.TextField(),
        ),
    ]