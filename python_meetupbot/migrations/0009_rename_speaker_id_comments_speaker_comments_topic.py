# Generated by Django 4.2.1 on 2023-06-25 09:43

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('python_meetupbot', '0008_remove_eventcomments_date_remove_questions_date'),
    ]

    operations = [
        migrations.RenameField(
            model_name='comments',
            old_name='speaker_id',
            new_name='speaker',
        ),
        migrations.AddField(
            model_name='comments',
            name='topic',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='topic', to='python_meetupbot.topics'),
        ),
    ]
