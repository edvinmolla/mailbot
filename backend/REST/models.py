from django.db import models

class default(models.Model):
    uemail = models.CharField(max_length=64)
    receiver = models.CharField(max_length=64)
    sender = models.CharField(max_length=64)
    subject = models.CharField(max_length=64)
    time = models.CharField(max_length=64)