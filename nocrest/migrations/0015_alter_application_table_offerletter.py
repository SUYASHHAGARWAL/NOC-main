# Generated by Django 5.0 on 2024-01-11 08:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nocrest', '0014_alter_application_table_offerletter'),
    ]

    operations = [
        migrations.AlterField(
            model_name='application_table',
            name='offerletter',
            field=models.FileField(default='', upload_to='Static/'),
        ),
    ]