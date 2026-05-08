Learning eventnest project

# env install

python -m venv .venv

# On windows
.venv\Scripts\activate

# On GitBash
source .venv/Scripts/activate

# On Mac/Linux
source .venv/bin/activate

pip install -r requirements.txt

python manage.py migrate

python manage.py runserver


python manage.py startapp appname apps/tickets


``
Ha, restructure kar do, pura project, such as events, categories, roles, etc.
Role, Dashboard(For admin), Home(for web) to separate app banega.. or recommend



apps/
  ├── accounts/          # Auth - model + web views + admin views
  │   ├── models.py
  │   ├── web_views.py   # login, register, profile
  │   ├── admin_views.py # user CRUD for panel or make separate app for understanding and consistency
  │   ├── web_urls.py
  │   ├── views.py # rahega  but blank for consistency
  │   ├── urls.py
  │   └── admin_urls.py
  │
  ├── events/            # Events - model + web views + admin views
  │   ├── models.py
  │   ├── migrations/
  │   ├── views.py # rahega  but blank for consistency
  │   ├── urls.py
  │   ├── web_views.py   # event list, detail, register
  │   ├── admin_views.py # admin CRUD
  │   ├── web_urls.py
  │   └── admin_urls.py


from django.urls import path, include

urlpatterns = [
    # User-facing URLs
    path('', include('apps.events.web_urls')),

    # Admin panel URLs
    path('', include('apps.events.admin_urls')),
]