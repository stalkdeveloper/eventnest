import os
import uuid
from django.conf import settings
from .models import Media


def get_media(obj, source_type):
    """
    Get a single media record for a given model instance and source type.
    Usage: get_media(user, 'profile_picture')
    """
    model_label = f"{obj._meta.app_label}.{obj.__class__.__name__}"
    return Media.objects.filter(
        mediable_type=model_label,
        mediable_id=obj.pk,
        source_type=source_type
    ).first()


def get_all_media(obj, source_type=None):
    """
    Get all media for an object, optionally filtered by source_type.
    Usage: get_all_media(event, 'event_gallery')
    """
    model_label = f"{obj._meta.app_label}.{obj.__class__.__name__}"
    qs = Media.objects.filter(mediable_type=model_label, mediable_id=obj.pk)
    if source_type:
        qs = qs.filter(source_type=source_type)
    return qs


def save_uploaded_file(file, obj, source_type, file_type=Media.FileType.IMAGE):
    """
    Save an uploaded file and create a Media record.
    """
    ext = os.path.splitext(file.name)[1].lower().lstrip('.')
    filename = f"{uuid.uuid4().hex}.{ext}"
    folder = f"{obj._meta.app_label}/{obj.__class__.__name__.lower()}/{source_type}/"
    relative_path = folder + filename
    full_path = os.path.join(settings.MEDIA_ROOT, relative_path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)

    with open(full_path, 'wb+') as dest:
        for chunk in file.chunks():
            dest.write(chunk)

    model_label = f"{obj._meta.app_label}.{obj.__class__.__name__}"
    media = Media.objects.create(
        mediable_type=model_label,
        mediable_id=obj.pk,
        source_type=source_type,
        storage_type=Media.StorageType.LOCAL,
        file_path=relative_path,
        original_file_name=file.name,
        file_type=file_type,
        extension=ext,
    )
    return media
