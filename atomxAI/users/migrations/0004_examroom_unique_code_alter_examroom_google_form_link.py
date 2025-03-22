from django.db import migrations, models
import random
import string

def generate_unique_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

def populate_unique_code(apps, schema_editor):
    ExamRoom = apps.get_model('users', 'ExamRoom')
    for room in ExamRoom.objects.all():
        if not room.unique_code:
            room.unique_code = generate_unique_code()
            room.save()

class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_alter_examroom_google_form_link'),
    ]

    operations = [
        migrations.AddField(
            model_name='examroom',
            name='unique_code',
            field=models.CharField(blank=True, max_length=10, unique=True),
        ),
        migrations.AlterField(
            model_name='examroom',
            name='google_form_link',
            field=models.URLField(default='https://www.google.com/'),
        ),
        migrations.RunPython(populate_unique_code),  # This will populate unique codes
    ]
