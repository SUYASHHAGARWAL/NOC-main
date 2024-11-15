# Generated by Django 4.2.7 on 2024-07-09 10:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nocrest', '0042_student_email_personal'),
    ]

    operations = [
        migrations.AddField(
            model_name='nodues_application_table',
            name='Dept_amount',
            field=models.CharField(default='', max_length=100),
        ),
        migrations.AddField(
            model_name='nodues_application_table',
            name='Exam_amount',
            field=models.CharField(default='', max_length=100),
        ),
        migrations.AddField(
            model_name='nodues_application_table',
            name='Genoffice_Comment',
            field=models.CharField(default='', max_length=100),
        ),
        migrations.AddField(
            model_name='nodues_application_table',
            name='Genoffice_amount',
            field=models.CharField(default='', max_length=100),
        ),
        migrations.AddField(
            model_name='nodues_application_table',
            name='Genoffice_approval',
            field=models.CharField(default='', max_length=12),
        ),
        migrations.AddField(
            model_name='nodues_application_table',
            name='Hostle_amount',
            field=models.CharField(default='', max_length=100),
        ),
        migrations.AddField(
            model_name='nodues_application_table',
            name='Lib_amount',
            field=models.CharField(default='', max_length=100),
        ),
        migrations.AddField(
            model_name='nodues_application_table',
            name='TnP_amount',
            field=models.CharField(default='', max_length=100),
        ),
    ]
