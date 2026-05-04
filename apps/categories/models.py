from django.db import models
from django.utils.text import slugify
from apps.core.mixins import TimeStampedModel, ActiveManager, AllObjectsManager


class Category(TimeStampedModel):
    parent      = models.ForeignKey(
        'self',
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='children',
    )
    title       = models.CharField(max_length=100)
    slug        = models.SlugField(unique=True, max_length=120)
    description = models.TextField(blank=True)
    color       = models.CharField(max_length=7, default='#6366f1')

    # managers
    objects     = ActiveManager()
    all_objects = AllObjectsManager()

    class Meta:
        verbose_name        = 'Category'
        verbose_name_plural = 'Categories'
        ordering            = ['title']

    def __str__(self):
        if self.parent:
            return f'{self.parent.title} › {self.title}'
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    @property
    def is_root(self):
        return self.parent_id is None

    def get_ancestors(self):
        """Return list of ancestors from root → self (not including self)."""
        ancestors = []
        node = self.parent
        while node:
            ancestors.insert(0, node)
            node = node.parent
        return ancestors

    def get_descendants(self):
        """Return all active descendant categories."""
        result = []
        for child in self.children.all():
            result.append(child)
            result.extend(child.get_descendants())
        return result
