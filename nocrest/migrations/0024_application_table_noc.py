# Generated by Django 4.2.7 on 2024-02-08 19:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nocrest', '0023_application_table_date_dept_approval_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='application_table',
            name='noc',
            field=models.CharField(default='', max_length=100),
        ),
    ]