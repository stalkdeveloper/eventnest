"""
Users seeder.
Creates default system and platform users for development/testing.
"""
from django.contrib.auth.models import Group


USERS_DATA = [
    {
        'username':     'superadmin',
        'email':        'admin@eventnest.com',
        'password':     'Admin@1234',
        'first_name':   'Super',
        'last_name':    'Admin',
        'is_staff':     True,
        'is_superuser': True,
        'account_type': 'system',
        'group':        'Admin',
    },
    {
        'username':     'subadmin1',
        'email':        'subadmin@eventnest.com',
        'password':     'Sub@12345',
        'first_name':   'Sub',
        'last_name':    'Admin',
        'is_staff':     True,
        'is_superuser': False,
        'account_type': 'system',
        'group':        'Admin',
    },
    {
        'username':     'organiser1',
        'email':        'organiser@eventnest.com',
        'password':     'Org@12345',
        'first_name':   'John',
        'last_name':    'Organiser',
        'is_staff':     False,
        'is_superuser': False,
        'account_type': 'platform',
        'group':        'Organiser',
    },
    {
        'username':     'guest_user',
        'email':        'guest@eventnest.com',
        'password':     'Guest@123',
        'first_name':   'Jane',
        'last_name':    'Guest',
        'is_staff':     False,
        'is_superuser': False,
        'account_type': 'platform',
        'group':        'Guest',
    },
]


def run(stdout=None):
    from apps.accounts.models import CustomUser

    def log(msg):
        if stdout:
            stdout.write(msg)

    for data in USERS_DATA:
        group_name   = data.pop('group')
        password     = data.pop('password')
        account_type = data.pop('account_type')

        if CustomUser.objects.filter(email=data['email']).exists():
            log(f"  Skipped (exists): {data['email']}")
            # restore popped keys for next iteration safety
            data['group'] = group_name
            data['password'] = password
            data['account_type'] = account_type
            continue

        user = CustomUser(**data)
        user.set_password(password)
        user.account_type = account_type
        user.save()

        user.groups.clear()
        group, _ = Group.objects.get_or_create(name=group_name)
        user.groups.add(group)

        log(f"  Created user: {user.email} [{group_name} / {account_type}]")

        # restore popped keys
        data['group']        = group_name
        data['password']     = password
        data['account_type'] = account_type
