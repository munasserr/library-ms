import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('library', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='loan',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='loans', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddIndex(
            model_name='book',
            index=models.Index(fields=['title'], name='library_boo_title_c38ef2_idx'),
        ),
        migrations.AddIndex(
            model_name='book',
            index=models.Index(fields=['author'], name='library_boo_author__e33dc7_idx'),
        ),
        migrations.AlterUniqueTogether(
            name='book',
            unique_together={('title', 'author', 'publish_date')},
        ),
        migrations.AddIndex(
            model_name='loan',
            index=models.Index(fields=['user'], name='library_loa_user_id_4ffac4_idx'),
        ),
        migrations.AddIndex(
            model_name='loan',
            index=models.Index(fields=['book'], name='library_loa_book_id_525a78_idx'),
        ),
        migrations.AlterUniqueTogether(
            name='loan',
            unique_together={('user', 'book', 'created')},
        ),
    ]
