import uuid

from django.db import models


# Create your models here.

class Merchant(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    file_name = models.CharField(max_length=255)
    tid = models.CharField(max_length=255, unique=True)
    aggregator_module = models.CharField(max_length=255)
    legal_name = models.CharField(max_length=255)
    primary_email = models.CharField(max_length=255)
    secondary_email = models.CharField(max_length=255)
    bcc_email = models.CharField(max_length=255, null=True, blank=True)
    creation_date_time = models.DateTimeField(auto_now_add=True)
    updated_date_time = models.DateTimeField(auto_now=True)



    def __str__(self):
        return self.tid + "-" + self.primary_email + "-" + self.aggregator_module



