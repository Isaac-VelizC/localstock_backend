from django.db import models
from django.utils import timezone

class SoftDeleteModel(models.Model):
    soft_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(blank=True, null=True)

    def delete(self, using = None, keep_parents = False):
        self.soft_deleted = True
        self.deleted_at = timezone.now()
        self.save()
    
    def hard_delete(self, using=None, keep_parents = False):
        super().delete(using=using, keep_parents=keep_parents)
    
    class Meta:
        abstract = True

class ActiveManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(soft_deleted=False)