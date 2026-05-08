"""
Categories seeder - root categories + nested children with level_type and entity_type.
"""

ROOT_CATEGORIES = [
    {'title': 'Music',         'slug': 'music',         'level_type': 'grand_parent', 'entity_type': 'events'},
    {'title': 'Technology',    'slug': 'technology',    'level_type': 'grand_parent', 'entity_type': 'events'},
    {'title': 'Business',      'slug': 'business',      'level_type': 'grand_parent', 'entity_type': 'events'},
    {'title': 'Arts & Culture','slug': 'arts-culture',  'level_type': 'grand_parent', 'entity_type': 'events'},
    {'title': 'Sports',        'slug': 'sports',        'level_type': 'grand_parent', 'entity_type': 'events'},
    {'title': 'Food & Drink',  'slug': 'food-drink',    'level_type': 'grand_parent', 'entity_type': 'events'},
    {'title': 'Education',     'slug': 'education',     'level_type': 'grand_parent', 'entity_type': 'events'},
    {'title': 'Health',        'slug': 'health',        'level_type': 'grand_parent', 'entity_type': 'events'},
]

# (parent_slug, title, slug, level_type, entity_type)
CHILD_CATEGORIES = [
    ('technology', 'Artificial Intelligence', 'ai',             'child', 'events'),
    ('technology', 'Web Development',         'web-dev',        'child', 'events'),
    ('technology', 'Cybersecurity',           'cybersecurity',  'child', 'events'),
    ('technology', 'Data Science',            'data-science',   'child', 'events'),

    ('music',      'Live Concerts',           'live-concerts',  'child', 'events'),
    ('music',      'DJ Nights',               'dj-nights',      'child', 'events'),
    ('music',      'Classical',               'classical',      'child', 'events'),

    ('business',   'Startups & VC',           'startups',       'child', 'events'),
    ('business',   'Finance & Investing',     'finance',        'child', 'events'),
    ('business',   'Marketing',               'marketing',      'child', 'events'),

    ('arts-culture','Photography',            'photography',    'child', 'events'),
    ('arts-culture','Theatre & Drama',        'theatre',        'child', 'events'),
    ('arts-culture','Painting & Sculpture',   'painting',       'child', 'events'),

    ('sports',     'Cricket',                 'cricket',        'child', 'events'),
    ('sports',     'Football',                'football',       'child', 'events'),
    ('sports',     'Running & Marathon',      'running',        'child', 'events'),

    ('food-drink', 'Street Food',             'street-food',    'child', 'events'),
    ('food-drink', 'Wine & Cocktails',        'wine',           'child', 'events'),

    ('education',  'Workshops',               'workshops',      'child', 'events'),
    ('education',  'Seminars',                'seminars',       'child', 'events'),

    ('health',     'Yoga & Wellness',         'yoga',           'child', 'events'),
    ('health',     'Mental Health',           'mental-health',  'child', 'events'),
]


def run(stdout=None):
    from apps.categories.models import Category

    def log(msg):
        if stdout:
            stdout.write(msg)

    cat_map = {}

    for c in ROOT_CATEGORIES:
        obj, created = Category.objects.get_or_create(
            slug=c['slug'],
            defaults={
                'title': c['title'],
                'level_type': c['level_type'],
                'entity_type': c['entity_type'],
            },
        )

        cat_map[c['slug']] = obj
        log(f"  {'Created' if created else 'Exists'} root (grand_parent): {c['title']}")


    for parent_slug, title, slug, level_type, entity_type in CHILD_CATEGORIES:
        parent = cat_map.get(parent_slug)

        if not parent:
            log(f"  Warning: Parent '{parent_slug}' not found, skipping {title}")
            continue

        obj, created = Category.objects.get_or_create(
            slug=slug,
            defaults={
                'title': title,
                'parent': parent,
                'level_type': level_type,
                'entity_type': entity_type,
            },
        )

        log(f"  {'Created' if created else 'Exists'} child ({level_type}): {title}")

    log("Seeder completed!")