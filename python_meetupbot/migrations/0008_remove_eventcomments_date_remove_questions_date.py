# Generated by Django 4.2.1 on 2023-06-25 08:14

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('python_meetupbot', '0007_questions_name'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='eventcomments',
            name='date',
        ),
        migrations.RemoveField(
            model_name='questions',
            name='date',
        ),
    ]
