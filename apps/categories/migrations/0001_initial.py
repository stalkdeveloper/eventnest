import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                
                ('parent', models.ForeignKey(
                    blank=True, 
                    null=True, 
                    on_delete=django.db.models.deletion.SET_NULL, 
                    related_name='children', 
                    to='categories.category'
                )),
                
                # Core fields
                ('title', models.CharField(max_length=100)),
                ('slug', models.SlugField(max_length=120, unique=True)),
                ('description', models.TextField(blank=True)),
                ('color', models.CharField(default='#6366f1', max_length=7)),
                
                ('level_type', models.CharField(
                    choices=[
                        ('grand_parent', 'Grand Parent'),
                        ('parent', 'Parent'),
                        ('child', 'Child'),
                    ],
                    default='grand_parent',
                    max_length=20,
                )),

                ('entity_type', models.CharField(
                    choices=[
                        ('events', 'Events'),
                        ('blog', 'Blog'),
                        ('both', 'Both'),
                    ],
                    default='events',
                    max_length=10,
                )),
                
                # Foreign keys
                ('created_by', models.ForeignKey(
                    blank=True, 
                    null=True, 
                    on_delete=django.db.models.deletion.SET_NULL, 
                    related_name='categories_category_created',
                    to=settings.AUTH_USER_MODEL
                )),
                ('deleted_by', models.ForeignKey(
                    blank=True, 
                    null=True, 
                    on_delete=django.db.models.deletion.SET_NULL, 
                    related_name='categories_category_deleted',
                    to=settings.AUTH_USER_MODEL
                )),
                ('updated_by', models.ForeignKey(
                    blank=True, 
                    null=True, 
                    on_delete=django.db.models.deletion.SET_NULL, 
                    related_name='categories_category_updated',
                    to=settings.AUTH_USER_MODEL
                )),
                
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('deleted_at', models.DateTimeField(blank=True, null=True)),
            ],
            options={
                'verbose_name': 'Category',
                'verbose_name_plural': 'Categories',
                'ordering': ['parent__title', 'title', 'level_type'],
            },
        ),
    ]