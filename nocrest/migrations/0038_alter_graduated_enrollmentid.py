# Generated by Django 4.2.7 on 2024-06-08 20:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nocrest', '0037_nodues_application_table_exam_comment_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='graduated',
            name='EnrollmentId',
            field=models.CharField(default='', max_length=12, unique=True),
        ),
    ]
