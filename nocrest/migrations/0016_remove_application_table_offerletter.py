# Generated by Django 5.0 on 2024-01-11 08:54

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('nocrest', '0015_alter_application_table_offerletter'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='application_table',
            name='offerletter',
        ),
    ]
