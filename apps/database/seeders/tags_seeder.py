"""
Tags seeder - creates a set of common event tags with distinct colours.
"""
from django.utils.text import slugify

TAGS_DATA = [
    {'name': 'Free Entry',   'color': '#10b981'},
    {'name': 'Featured',     'color': '#f59e0b'},
    {'name': 'Networking',   'color': '#6366f1'},
    {'name': 'Workshop',     'color': '#8b5cf6'},
    {'name': 'Outdoor',      'color': '#22c55e'},
    {'name': 'Online',       'color': '#06b6d4'},
    {'name': 'Family',       'color': '#f97316'},
    {'name': 'Students',     'color': '#3b82f6'},
    {'name': 'Food',         'color': '#ef4444'},
    {'name': 'Music',        'color': '#ec4899'},
    {'name': 'Tech',         'color': '#7c3aed'},
    {'name': 'Sports',       'color': '#14b8a6'},
    {'name': 'Art',          'color': '#d946ef'},
    {'name': 'Business',     'color': '#64748b'},
    {'name': 'Wellness',     'color': '#84cc16'},
]


def run(stdout=None):
    from apps.events.models import Tag

    def log(msg):
        if stdout:
            stdout.write(msg)

    for data in TAGS_DATA:
        slug = slugify(data['name'])
        tag, created = Tag.objects.get_or_create(
            slug=slug,
            defaults={'name': data['name'], 'color': data['color']},
        )
        log(f"  {'Created' if created else 'Exists '} tag: {tag.name} ({tag.color})")

    log('  Tags seeder complete.')
