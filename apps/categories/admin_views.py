from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils.text import slugify
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator
from apps.core.decorators import system_required
from .models import Category
from apps.events.models import Event


@system_required
def category_list(request):
    root_cats = Category.objects.filter(parent=None).prefetch_related(
        'children__children__children'
    )
    all_cats = []
    for root in root_cats:
        all_cats.append(root)
        all_cats.extend(root.get_descendants())

    paginator   = Paginator(all_cats, 20)
    cats        = paginator.get_page(request.GET.get('page'))

    return render(request, 'categories/admin/list.html', {
        'categories':  cats,
        'LEVEL_TYPES': Category.LEVEL_TYPES,
        'ENTITY_TYPES': Category.ENTITY_TYPES,
    })


@system_required
def category_detail(request, cat_id):
    cat      = get_object_or_404(Category.all_objects, pk=cat_id)
    children = Category.all_objects.filter(parent=cat).select_related('parent')
    events   = (
        Event.all_objects
        .filter(category=cat)
        .select_related('organiser')
        .order_by('-created_at')[:10]
    )
    return render(request, 'categories/admin/detail.html', {
        'cat': cat, 'children': children, 'events': events,
    })


@system_required
def category_create(request):
    root_cats = Category.objects.filter(parent=None)
    if request.method == 'POST':
        title       = request.POST.get('title', '').strip()
        slug        = request.POST.get('slug', '').strip() or slugify(title)
        color       = request.POST.get('color', '#6366f1')
        desc        = request.POST.get('description', '')
        parent_id   = request.POST.get('parent')
        parent      = Category.objects.filter(pk=parent_id).first() if parent_id else None
        level_type  = request.POST.get('level_type', 'grand_parent')
        entity_type = request.POST.get('entity_type', 'events')

        if Category.objects.filter(slug=slug).exists():
            messages.error(request, f'Slug "{slug}" already exists.')
        else:
            cat = Category.objects.create(
                title=title, slug=slug, description=desc,
                color=color, parent=parent, created_by=request.user,
                level_type=level_type, entity_type=entity_type,
            )
            messages.success(request, f'Category "{cat.title}" created.')
            return redirect('admin_categories:category_list')
    return render(request, 'categories/admin/form.html', {
        'action': 'Create', 'title': 'Create Category',
        'root_cats':   root_cats,
        'LEVEL_TYPES': Category.LEVEL_TYPES,
        'ENTITY_TYPES': Category.ENTITY_TYPES,
    })


@system_required
def category_edit(request, cat_id):
    cat       = get_object_or_404(Category.all_objects, pk=cat_id)
    root_cats = Category.objects.filter(parent=None).exclude(pk=cat.pk)
    if request.method == 'POST':
        cat.title       = request.POST.get('title', cat.title).strip()
        cat.slug        = request.POST.get('slug', '').strip() or slugify(cat.title)
        cat.description = request.POST.get('description', '')
        cat.level_type  = request.POST.get('level_type', cat.level_type)
        cat.entity_type = request.POST.get('entity_type', cat.entity_type)
        cat.updated_by  = request.user
        parent_id       = request.POST.get('parent')
        cat.parent      = Category.objects.filter(pk=parent_id).first() if parent_id else None
        cat.save()
        messages.success(request, f'Category "{cat.title}" updated.')
        return redirect('admin_categories:category_list')
    return render(request, 'categories/admin/form.html', {
        'action': 'Edit', 'title': f'Edit - {cat.title}',
        'cat':         cat,
        'root_cats':   root_cats,
        'LEVEL_TYPES': Category.LEVEL_TYPES,
        'ENTITY_TYPES': Category.ENTITY_TYPES,
    })


@system_required
@require_POST
def category_delete(request, cat_id):
    cat = get_object_or_404(Category.all_objects, pk=cat_id)
    if cat.deleted_at:
        cat.restore()
        messages.success(request, f'"{cat.title}" restored.')
    else:
        cat.soft_delete(user=request.user)
        messages.success(request, f'"{cat.title}" deleted.')
    return redirect('admin_categories:category_list')
