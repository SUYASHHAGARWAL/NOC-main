# Generated by Django 4.2.7 on 2024-04-30 22:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nocrest', '0028_application_table_allow_edit'),
    ]

    operations = [
        migrations.CreateModel(
            name='Bonafide',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('student_name', models.CharField(default='', max_length=50)),
                ('EnrollmentId', models.CharField(default='', max_length=50)),
                ('fathers_name', models.CharField(default='', max_length=50)),
                ('Semester', models.CharField(default='', max_length=50)),
                ('email', models.CharField(default='', max_length=50)),
                ('session', models.CharField(default='', max_length=50)),
                ('application_date', models.CharField(default='', max_length=20)),
                ('approval_date', models.CharField(default='', max_length=20)),
                ('app_id', models.CharField(default='', max_length=20)),
                ('dept_approval', models.CharField(default='', max_length=20)),
                ('dept_comment', models.CharField(default='', max_length=20)),
            ],
        ),
    ]
