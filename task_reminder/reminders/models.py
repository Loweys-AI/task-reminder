from django.contrib.auth.models import User
from django.db import models

class Reminder(models.Model):
    PRIORITY_CHOICES = [
        ('high', 'High'),
        ('medium', 'Medium'),
        ('low', 'Low')
    ]
    CATEGORY_CHOICES = [
        ('work', 'Work'),
        ('home', 'Home'),
        ('personal', 'Personal')
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    due_time = models.DateTimeField()
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    category = models.CharField(max_length=10, choices=CATEGORY_CHOICES, default='personal')
    completed = models.BooleanField(default=False)
    recurring = models.CharField(max_length=50, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)