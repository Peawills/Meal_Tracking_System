# Generated migration: add performed_by FK to FeedingRecord
from django.db import migrations, models
import django.conf


class Migration(migrations.Migration):
    dependencies = [
        ("students", "0004_add_manual_fields"),
    ]

    operations = [
        migrations.AddField(
            model_name="feedingrecord",
            name="performed_by",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=models.SET_NULL,
                to=django.conf.settings.AUTH_USER_MODEL,
            ),
        ),
    ]
