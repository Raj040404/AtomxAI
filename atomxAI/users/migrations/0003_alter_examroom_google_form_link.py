# Generated by Django 5.1.1 on 2024-10-11 11:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_examroom_exam_duration_examroom_google_form_link_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='examroom',
            name='google_form_link',
            field=models.URLField(default=''),
        ),
    ]
