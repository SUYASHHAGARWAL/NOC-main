# Generated by Django 4.2.4 on 2023-11-24 08:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nocrest', '0011_graduated'),
    ]

    operations = [
        migrations.AddField(
            model_name='application_table',
            name='Designation_reciever',
            field=models.CharField(default='', max_length=60),
        ),
        migrations.AddField(
            model_name='application_table',
            name='apply_through',
            field=models.CharField(default='', max_length=150),
        ),
        migrations.AddField(
            model_name='application_table',
            name='declaration',
            field=models.CharField(default='', max_length=150),
        ),
        migrations.AddField(
            model_name='application_table',
            name='duration',
            field=models.CharField(default='', max_length=40),
        ),
        migrations.AddField(
            model_name='application_table',
            name='endDate',
            field=models.CharField(default='', max_length=40),
        ),
        migrations.AddField(
            model_name='application_table',
            name='location',
            field=models.CharField(default='', max_length=35),
        ),
        migrations.AddField(
            model_name='application_table',
            name='name_reciever',
            field=models.CharField(default='', max_length=60),
        ),
        migrations.AddField(
            model_name='application_table',
            name='offerletter',
            field=models.FileField(default='', upload_to='Static/'),
        ),
        migrations.AddField(
            model_name='application_table',
            name='org_address',
            field=models.CharField(default='', max_length=150),
        ),
        migrations.AddField(
            model_name='application_table',
            name='startDate',
            field=models.CharField(default='', max_length=40),
        ),
        migrations.AddField(
            model_name='application_table',
            name='stipend',
            field=models.CharField(default='', max_length=150),
        ),
        migrations.AddField(
            model_name='application_table',
            name='websitr_org',
            field=models.CharField(default='', max_length=150),
        ),
        migrations.AddField(
            model_name='application_table',
            name='year',
            field=models.CharField(default='', max_length=35),
        ),
    ]
