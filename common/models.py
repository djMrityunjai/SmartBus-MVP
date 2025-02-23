from django.db import models
from django.conf import settings
from django.utils import timezone

# Create your models here.

class BaseMixin(models.Model):
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='%(class)s_created',
        editable=False
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='%(class)s_updated',
        editable=False
    )
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    remarks = models.TextField(blank=True, null=True)

    class Meta:
        abstract = True
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        if not self.pk:  # New instance
            self.created_at = timezone.now()
            if user:
                self.created_by = user
        
        self.updated_at = timezone.now()
        if user:
            self.updated_by = user
            
        super().save(*args, **kwargs)

class AddressMixin(models.Model):
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    zip_code = models.CharField(max_length=10, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    class Meta:
        abstract = True
