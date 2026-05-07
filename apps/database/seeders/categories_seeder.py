"""
Categories seeder — root categories + nested children.
"""

ROOT_CATEGORIES = [
    {'title': 'Music',        'slug': 'music',        'color': '#ec4899'},
    {'title': 'Technology',   'slug': 'technology',   'color': '#6366f1'},
    {'title': 'Business',     'slug': 'business',     'color': '#f59e0b'},
    {'title': 'Arts & Culture','slug': 'arts-culture', 'color': '#10b981'},
    {'title': 'Sports',       'slug': 'sports',       'color': '#ef4444'},
    {'title': 'Food & Drink', 'slug': 'food-drink',   'color': '#f97316'},
    {'title': 'Education',    'slug': 'education',    'color': '#8b5cf6'},
    {'title': 'Health',       'slug': 'health',       'color': '#06b6d4'},
]

# (parent_slug, title, slug, color)
CHILD_CATEGORIES = [
    ('technology', 'Artificial Intelligence', 'ai',            '#818cf8'),
    ('technology', 'Web Development',         'web-dev',       '#a78bfa'),
    ('technology', 'Cybersecurity',           'cybersecurity', '#c4b5fd'),
    ('technology', 'Data Science',            'data-science',  '#7c3aed'),
    ('music',      'Live Concerts',           'live-concerts', '#f472b6'),
    ('music',      'DJ Nights',               'dj-nights',     '#fb7185'),
    ('music',      'Classical',               'classical',     '#f9a8d4'),
    ('business',   'Startups & VC',           'startups',      '#fbbf24'),
    ('business',   'Finance & Investing',     'finance',       '#fcd34d'),
    ('business',   'Marketing',               'marketing',     '#f59e0b'),
    ('arts-culture','Photography',            'photography',   '#34d399'),
    ('arts-culture','Theatre & Drama',        'theatre',       '#6ee7b7'),
    ('arts-culture','Painting & Sculpture',   'painting',      '#10b981'),
    ('sports',     'Cricket',                 'cricket',       '#f87171'),
    ('sports',     'Football',                'football',      '#fca5a5'),
    ('sports',     'Running & Marathon',      'running',       '#ef4444'),
    ('food-drink', 'Street Food',             'street-food',   '#fb923c'),
    ('food-drink', 'Wine & Cocktails',        'wine',          '#f97316'),
    ('education',  'Workshops',               'workshops',     '#a78bfa'),
    ('education',  'Seminars',                'seminars',      '#8b5cf6'),
    ('health',     'Yoga & Wellness',         'yoga',          '#22d3ee'),
    ('health',     'Mental Health',           'mental-health', '#06b6d4'),
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
            defaults={'title': c['title'], 'color': c['color']},
        )
        cat_map[c['slug']] = obj
        log(f"  {'Created' if created else 'Exists'} root: {c['title']}")

    for parent_slug, title, slug, color in CHILD_CATEGORIES:
        parent = cat_map.get(parent_slug)
        obj, created = Category.objects.get_or_create(
            slug=slug,
            defaults={
                'title': title, 'slug': slug,
                'color': color, 'parent': parent,
            },
        )
        log(f"  {'Created' if created else 'Exists'} child: {title}")
