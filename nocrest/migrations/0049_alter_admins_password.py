# Generated by Django 4.2.7 on 2024-07-28 21:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nocrest', '0048_alter_student_password'),
    ]

    operations = [
        migrations.AlterField(
            model_name='admins',
            name='Password',
            field=models.CharField(default='', max_length=255),
        ),
    ]
