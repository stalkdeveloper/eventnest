from django.shortcuts import render, get_object_or_404
from .models import Category
from apps.events.models import Event


def category_list(request):
    categories = Category.objects.filter(parent=None)
    return render(request, 'categories/web/list.html', {'categories': categories})


def category_detail(request, slug):
    cat    = get_object_or_404(Category, slug=slug)
    events = Event.objects.filter(category=cat, status='published').order_by('-start_date')
    return render(request, 'categories/web/detail.html', {'cat': cat, 'events': events})
