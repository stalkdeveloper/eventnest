from django.db import models
from django.utils.text import slugify
from apps.core.mixins import TimeStampedModel, ActiveManager, AllObjectsManager


class Category(TimeStampedModel):
    parent = models.ForeignKey(
        'self',
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='children',
    )
    title = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, max_length=120)
    description = models.TextField(blank=True)
    
    LEVEL_TYPES = [
        ('grand_parent', 'Grand Parent'),
        ('parent', 'Parent'),
        ('child', 'Child'),
    ]
    ENTITY_TYPES = [
        ('events', 'Events'),
        ('blog', 'Blog'),
        ('both', 'Both'),
    ]
    
    level_type = models.CharField(max_length=20, choices=LEVEL_TYPES, default='grand_parent')
    entity_type = models.CharField(max_length=10, choices=ENTITY_TYPES, default='events')

    # managers
    objects = ActiveManager()
    all_objects = AllObjectsManager()

    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
        ordering = ['parent__title', 'title', 'level_type']

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

    def get_level(self):
        """Calculate hierarchy level: 0=grand_parent, 1=parent, 2+=child."""
        level = 0
        node = self
        while node.parent:
            level += 1
            node = node.parent
        return level

    def get_level_indent(self):
        """Indentation for tree display (rem units)."""
        return self.get_level() * 1.5

    @property
    def level_type_computed(self):
        """Auto-compute level_type based on hierarchy if not set."""
        if self.level_type != 'grand_parent':
            level = self.get_level()
            if level == 0:
                return 'grand_parent'
            elif level == 1:
                return 'parent'
            else:
                return 'child'
        return self.level_type

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