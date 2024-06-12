from django.db import models

class EmailLog(models.Model):
        recipient = models.EmailField()   
        timestamp = models.DateTimeField(auto_now_add=True)

