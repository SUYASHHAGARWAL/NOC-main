# Generated by Django 4.2.4 on 2023-09-21 09:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nocrest', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='student',
            name='password',
            field=models.CharField(default=0, max_length=120),
        ),
        migrations.AddField(
            model_name='student',
            name='username',
            field=models.CharField(default=0, max_length=120),
        ),
    ]