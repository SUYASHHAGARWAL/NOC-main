# Generated by Django 5.0 on 2024-01-13 09:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nocrest', '0020_alter_application_table_offerletter'),
    ]

    operations = [
        migrations.AddField(
            model_name='application_table',
            name='Time_Dept_approval',
            field=models.CharField(default='', max_length=100),
        ),
        migrations.AddField(
            model_name='application_table',
            name='Time_Tnp_approval',
            field=models.CharField(default='', max_length=100),
        ),
    ]