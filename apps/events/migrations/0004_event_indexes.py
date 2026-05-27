from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0003_alter_event_created_by_alter_event_deleted_by_and_more'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='event',
            index=models.Index(fields=['status', 'start_date'], name='events_event_status_start_idx'),
        ),
        migrations.AddIndex(
            model_name='event',
            index=models.Index(fields=['organiser', 'status'], name='events_event_organiser_status_idx'),
        ),
        migrations.AddIndex(
            model_name='event',
            index=models.Index(fields=['is_featured', 'status'], name='events_event_featured_status_idx'),
        ),
        migrations.AddIndex(
            model_name='event',
            index=models.Index(fields=['is_free', 'status'], name='events_event_free_status_idx'),
        ),
        migrations.AddIndex(
            model_name='event',
            index=models.Index(fields=['city'], name='events_event_city_idx'),
        ),
    ]
