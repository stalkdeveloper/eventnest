from django.apps import AppConfig

class MediaConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.media"         # full dotted path
    label = "media"             # short label Django uses internally