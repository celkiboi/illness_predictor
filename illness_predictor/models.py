from django.db import models
from django.contrib.auth.models import User

from django.db import models
from django.contrib.auth.models import User

class IllnessPrediction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    symptoms = models.JSONField()
    predictions = models.JSONField()
