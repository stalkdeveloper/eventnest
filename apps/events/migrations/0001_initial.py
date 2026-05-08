import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('categories', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                
                ('title', models.CharField(max_length=255)),
                ('slug', models.SlugField(max_length=255, unique=True)),
                ('description', models.TextField()),
                ('event_type', models.CharField(choices=[('online', 'Online'), ('offline', 'Offline'), ('hybrid', 'Hybrid')], default='offline', max_length=10)),
                ('status', models.CharField(choices=[('draft', 'Draft'), ('published', 'Published'), ('cancelled', 'Cancelled'), ('completed', 'Completed')], default='draft', max_length=15)),
                ('start_date', models.DateTimeField()),
                ('end_date', models.DateTimeField()),
                ('venue', models.CharField(blank=True, max_length=255)),
                ('city', models.CharField(blank=True, max_length=100)),
                ('address', models.TextField(blank=True)),
                ('online_link', models.URLField(blank=True)),
                ('max_capacity', models.PositiveIntegerField(default=0)),
                ('ticket_price', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
                ('is_free', models.BooleanField(default=True)),
                ('is_featured', models.BooleanField(default=False)),
                ('category', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='events', to='categories.category')),
                ('organiser', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='organised_events', to=settings.AUTH_USER_MODEL)),

                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='events_event_created', to=settings.AUTH_USER_MODEL)),
                ('updated_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='events_event_updated', to=settings.AUTH_USER_MODEL)),
                ('deleted_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='events_event_deleted', to=settings.AUTH_USER_MODEL)),

                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('deleted_at', models.DateTimeField(blank=True, null=True)),
            ],
            options={
                'ordering': ['-start_date'],
            },
        ),
    ]