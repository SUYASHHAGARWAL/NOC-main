# Generated by Django 4.2.4 on 2023-10-12 11:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nocrest', '0004_alter_application_table_company_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='admins',
            name='dept',
            field=models.CharField(default='', max_length=15),
        ),
    ]
