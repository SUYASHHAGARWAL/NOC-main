# Generated by Django 4.2.4 on 2023-10-25 05:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nocrest', '0007_alter_admins_email'),
    ]

    operations = [
        migrations.AddField(
            model_name='application_table',
            name='App_Date',
            field=models.CharField(default='', max_length=100),
        ),
        migrations.AddField(
            model_name='application_table',
            name='App_time',
            field=models.CharField(default='', max_length=100),
        ),
    ]