# Generated by Django 4.2.7 on 2024-02-10 14:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nocrest', '0024_application_table_noc'),
    ]

    operations = [
        migrations.AddField(
            model_name='department',
            name='Department',
            field=models.CharField(default='', max_length=120),
        ),
    ]