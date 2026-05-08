"""
Categories seeder - root categories + nested children with level_type and entity_type.
"""

ROOT_CATEGORIES = [
    {'title': 'Music',        'slug': 'music',        'color': '#ec4899', 'level_type': 'grand_parent', 'entity_type': 'events'},
    {'title': 'Technology',   'slug': 'technology',   'color': '#6366f1', 'level_type': 'grand_parent', 'entity_type': 'events'},
    {'title': 'Business',     'slug': 'business',     'color': '#f59e0b', 'level_type': 'grand_parent', 'entity_type': 'events'},
    {'title': 'Arts & Culture','slug': 'arts-culture', 'color': '#10b981', 'level_type': 'grand_parent', 'entity_type': 'events'},
    {'title': 'Sports',       'slug': 'sports',       'color': '#ef4444', 'level_type': 'grand_parent', 'entity_type': 'events'},
    {'title': 'Food & Drink', 'slug': 'food-drink',   'color': '#f97316', 'level_type': 'grand_parent', 'entity_type': 'events'},
    {'title': 'Education',    'slug': 'education',    'color': '#8b5cf6', 'level_type': 'grand_parent', 'entity_type': 'events'},
    {'title': 'Health',       'slug': 'health',       'color': '#06b6d4', 'level_type': 'grand_parent', 'entity_type': 'events'},
]

# (parent_slug, title, slug, color, level_type, entity_type)
CHILD_CATEGORIES = [
    ('technology', 'Artificial Intelligence', 'ai',            '#818cf8', 'child', 'events'),
    ('technology', 'Web Development',         'web-dev',       '#a78bfa', 'child', 'events'),
    ('technology', 'Cybersecurity',           'cybersecurity', '#c4b5fd', 'child', 'events'),
    ('technology', 'Data Science',            'data-science',  '#7c3aed', 'child', 'events'),
    ('music',      'Live Concerts',           'live-concerts', '#f472b6', 'child', 'events'),
    ('music',      'DJ Nights',               'dj-nights',     '#fb7185', 'child', 'events'),
    ('music',      'Classical',               'classical',     '#f9a8d4', 'child', 'events'),
    ('business',   'Startups & VC',           'startups',      '#fbbf24', 'child', 'events'),
    ('business',   'Finance & Investing',     'finance',       '#fcd34d', 'child', 'events'),
    ('business',   'Marketing',               'marketing',     '#f59e0b', 'child', 'events'),
    ('arts-culture','Photography',            'photography',   '#34d399', 'child', 'events'),
    ('arts-culture','Theatre & Drama',        'theatre',       '#6ee7b7', 'child', 'events'),
    ('arts-culture','Painting & Sculpture',   'painting',      '#10b981', 'child', 'events'),
    ('sports',     'Cricket',                 'cricket',       '#f87171', 'child', 'events'),
    ('sports',     'Football',                'football',      '#fca5a5', 'child', 'events'),
    ('sports',     'Running & Marathon',      'running',       '#ef4444', 'child', 'events'),
    ('food-drink', 'Street Food',             'street-food',   '#fb923c', 'child', 'events'),
    ('food-drink', 'Wine & Cocktails',        'wine',          '#f97316', 'child', 'events'),
    ('education',  'Workshops',               'workshops',     '#a78bfa', 'child', 'events'),
    ('education',  'Seminars',                'seminars',      '#8b5cf6', 'child', 'events'),
    ('health',     'Yoga & Wellness',         'yoga',          '#22d3ee', 'child', 'events'),
    ('health',     'Mental Health',           'mental-health', '#06b6d4', 'child', 'events'),
]

def run(stdout=None):
    from apps.categories.models import Category

    def log(msg):
        if stdout:
            stdout.write(msg)

    cat_map = {}

    # Create root categories (grand_parent)
    for c in ROOT_CATEGORIES:
        obj, created = Category.objects.get_or_create(
            slug=c['slug'],
            defaults={
                'title': c['title'], 
                'color': c['color'],
                'level_type': c['level_type'],
                'entity_type': c['entity_type'],
            },
        )
        cat_map[c['slug']] = obj
        log(f"  {'Created' if created else 'Exists'} root (grand_parent): {c['title']}")

    # Create child categories
    for parent_slug, title, slug, color, level_type, entity_type in CHILD_CATEGORIES:
        parent = cat_map.get(parent_slug)
        if not parent:
            log(f"  Warning: Parent '{parent_slug}' not found, skipping {title}")
            continue
            
        obj, created = Category.objects.get_or_create(
            slug=slug,
            defaults={
                'title': title, 
                'color': color, 
                'parent': parent,
                'level_type': level_type,
                'entity_type': entity_type,
            },
        )
        log(f"  {'Created' if created else 'Exists'} child ({level_type}): {title}")

    log("Seeder completed!")