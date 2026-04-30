import os
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from .models import Media
from .utils import save_uploaded_file


@login_required
@require_POST
def upload(request):
    """
    Generic file upload endpoint.
    POST params:
      - file         : the uploaded file
      - mediable_type: e.g. "accounts.CustomUser"
      - mediable_id  : PK of the owning object
      - source_type  : e.g. "profile_picture"
      - file_type    : image | video | document | audio | other  (default: image)
    """
    file = request.FILES.get('file')
    if not file:
        return JsonResponse({'error': 'No file provided.'}, status=400)

    mediable_type = request.POST.get('mediable_type', '')
    mediable_id   = request.POST.get('mediable_id', 0)
    source_type   = request.POST.get('source_type', 'upload')
    file_type     = request.POST.get('file_type', Media.FileType.IMAGE)

    # Security: users can only upload to their own records unless staff
    if mediable_type == 'accounts.CustomUser' and not request.user.is_staff:
        if str(request.user.pk) != str(mediable_id):
            return JsonResponse({'error': 'Permission denied.'}, status=403)

    # Build a minimal proxy object so save_uploaded_file can derive the label
    class _Proxy:
        class _meta:
            app_label = mediable_type.split('.')[0] if '.' in mediable_type else 'unknown'
        __class__ = type('_Proxy', (), {'__name__': mediable_type.split('.')[-1] if '.' in mediable_type else 'Unknown'})()
        pk = mediable_id

    try:
        media = save_uploaded_file(file, _Proxy(), source_type, file_type)
        return JsonResponse({
            'id':       media.pk,
            'url':      media.get_url(),
            'filename': media.original_file_name,
            'type':     media.file_type,
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@require_POST
def upload_profile_picture(request):
    """Dedicated endpoint for profile picture uploads."""
    file = request.FILES.get('file')
    if not file:
        return JsonResponse({'error': 'No file provided.'}, status=400)

    # Remove old profile picture
    Media.objects.filter(
        mediable_type='accounts.CustomUser',
        mediable_id=request.user.pk,
        source_type='profile_picture'
    ).delete()

    media = save_uploaded_file(file, request.user, 'profile_picture', Media.FileType.IMAGE)
    return JsonResponse({'id': media.pk, 'url': media.get_url()})
