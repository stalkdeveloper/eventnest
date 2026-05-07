"""
Groups seeder — uses Django's built-in default permissions.
No custom permissions are created; we rely on the auto-generated
add_*, change_*, delete_*, view_* permissions Django creates.
"""
from django.contrib.auth.models import Group
from django.contrib.contenttypes.models import ContentType


# Map: group name → list of (app_label, model_name, action)
GROUP_PERMISSIONS = {
    'Admin': [
        # Events
        ('events', 'event',  'add'),    ('events', 'event',  'change'),
        ('events', 'event',  'delete'), ('events', 'event',  'view'),
        ('events', 'ticket', 'add'),    ('events', 'ticket', 'change'),
        ('events', 'ticket', 'delete'), ('events', 'ticket', 'view'),
        # Categories
        ('categories', 'category', 'add'),    ('categories', 'category', 'change'),
        ('categories', 'category', 'delete'), ('categories', 'category', 'view'),
        # Users
        ('accounts', 'customuser', 'add'),    ('accounts', 'customuser', 'change'),
        ('accounts', 'customuser', 'delete'), ('accounts', 'customuser', 'view'),
    ],
    'Organiser': [
        ('events', 'event',  'add'), ('events', 'event', 'change'), ('events', 'event', 'view'),
        ('events', 'ticket', 'view'),
        ('categories', 'category', 'view'),
    ],
    'Guest': [
        ('events', 'event',  'view'),
        ('events', 'ticket', 'add'), ('events', 'ticket', 'view'),
    ],
}


def run(stdout=None):
    from django.contrib.auth.models import Permission

    def log(msg):
        if stdout:
            stdout.write(msg)

    for group_name, perm_tuples in GROUP_PERMISSIONS.items():
        group, created = Group.objects.get_or_create(name=group_name)
        group.permissions.clear()

        for app_label, model_name, action in perm_tuples:
            try:
                ct   = ContentType.objects.get(app_label=app_label, model=model_name)
                perm = Permission.objects.get(codename=f'{action}_{model_name}', content_type=ct)
                group.permissions.add(perm)
            except (ContentType.DoesNotExist, Permission.DoesNotExist):
                log(f'    [warn] permission {action}_{model_name} not found')

        log(f"  {'Created' if created else 'Updated'} group: {group_name}")
