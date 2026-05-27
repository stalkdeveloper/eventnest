from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tickets', '0002_alter_ticket_created_by_alter_ticket_deleted_by_and_more'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='ticket',
            index=models.Index(fields=['attendee', 'status'], name='tickets_ticket_attendee_status_idx'),
        ),
        migrations.AddIndex(
            model_name='ticket',
            index=models.Index(fields=['event', 'status'], name='tickets_ticket_event_status_idx'),
        ),
        migrations.AddIndex(
            model_name='ticket',
            index=models.Index(fields=['ticket_code'], name='tickets_ticket_code_idx'),
        ),
    ]
