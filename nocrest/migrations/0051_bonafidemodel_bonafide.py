# Generated by Django 4.2.7 on 2024-08-03 12:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nocrest', '0050_department_displayname'),
    ]

    operations = [
        migrations.AddField(
            model_name='bonafidemodel',
            name='bonafide',
            field=models.CharField(default='', max_length=100),
        ),
    ]
