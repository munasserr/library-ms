from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('library', '0002_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='book',
            name='is_available',
            field=models.BooleanField(default=True),
        ),
    ]
