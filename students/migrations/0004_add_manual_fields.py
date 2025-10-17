# Generated migration: add auth_method, reason, notes to FeedingRecord
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("students", "0003_alter_feedingrecord_date_alter_feedingrecord_time"),
    ]

    operations = [
        migrations.AddField(
            model_name="feedingrecord",
            name="auth_method",
            field=models.CharField(
                choices=[
                    ("scanner", "Scanner/Card"),
                    ("manual", "Manual"),
                    ("other", "Other"),
                ],
                default="scanner",
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name="feedingrecord",
            name="reason",
            field=models.CharField(max_length=255, null=True, blank=True),
        ),
        migrations.AddField(
            model_name="feedingrecord",
            name="notes",
            field=models.TextField(null=True, blank=True),
        ),
    ]
