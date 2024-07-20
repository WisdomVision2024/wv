# Generated by Django 4.2.13 on 2024-06-02 10:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0007_alter_userdata_email_alter_userdata_name_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userdata',
            name='Email',
            field=models.EmailField(blank=True, default='', max_length=50),
        ),
        migrations.AlterField(
            model_name='userdata',
            name='Name',
            field=models.CharField(max_length=20),
        ),
        migrations.AlterField(
            model_name='userdata',
            name='Phone',
            field=models.CharField(max_length=50),
        ),
        migrations.AlterField(
            model_name='userdata',
            name='identity',
            field=models.CharField(default='Y', max_length=2),
        ),
    ]