from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("medsite", "0022_remove_appointment_reason_appointment_diagnoses_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="appointment",
            name="reason",
            field=models.TextField(
                max_length=100, blank=True, null=True, verbose_name="Причина обращения"
            ),
        ),
    ]
