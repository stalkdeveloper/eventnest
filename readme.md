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