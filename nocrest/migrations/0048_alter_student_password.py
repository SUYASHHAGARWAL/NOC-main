# Generated by Django 4.2.7 on 2024-07-28 18:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nocrest', '0047_exitsurvey_stipenddocproof'),
    ]

    operations = [
        migrations.AlterField(
            model_name='student',
            name='password',
            field=models.CharField(default=0, max_length=255),
        ),
    ]