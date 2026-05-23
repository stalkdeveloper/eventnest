import os
import sys

project_home = "/home/hiplstaging2/public_html/eventnest.hipl-staging2.com/"

if project_home not in sys.path:
    sys.path.insert(0, project_home)

activate_this = '/home/hiplstaging2/public_html/eventnest.hipl-staging2.com/eventnest/bin/activate_this.py'
with open(activate_this) as file_:
    exec(file_.read(), dict(__file__=activate_this))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "eventnest.settings")

from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()
