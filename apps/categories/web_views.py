from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Count, Q
from .models import Category
from apps.events.models import Event


def category_list(request):
    # Annotate root categories with published event counts (one query via subquery)
    categories = (
        Category.objects
        .filter(parent=None)
        .prefetch_related('children__children')
    )

    cat_list = []
    for cat in categories:
        all_ids = [cat.id] + [c.id for c in cat.get_descendants()]
        total   = Event.objects.filter(category_id__in=all_ids, status='published').count()
        cat.total_event_count = total
        cat_list.append(cat)

    return render(request, 'categories/web/list.html', {'categories': cat_list})


def category_detail(request, slug):
    cat      = get_object_or_404(Category, slug=slug)
    all_cats = [cat] + cat.get_descendants()
    all_cat_ids = [c.id for c in all_cats]

    events_qs = (
        Event.objects
        .filter(category_id__in=all_cat_ids, status='published')
        .order_by('-start_date')
        .select_related('category')
        .prefetch_related('tags')
    )

    paginator = Paginator(events_qs, 12)
    page_obj  = paginator.get_page(request.GET.get('page'))

    return render(request, 'categories/web/detail.html', {
        'cat':          cat,
        'subcategories': all_cats[1:],
        'events':       page_obj,
        'page_obj':     page_obj,
        'total_events': events_qs.count(),
    })
