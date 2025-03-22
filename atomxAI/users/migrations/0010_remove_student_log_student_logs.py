# Generated by Django 5.1.1 on 2024-10-20 14:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0009_student_log'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='student',
            name='log',
        ),
        migrations.AddField(
            model_name='student',
            name='logs',
            field=models.JSONField(blank=True, default=list),
        ),
    ]
