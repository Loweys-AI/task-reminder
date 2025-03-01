from django.utils import timezone
from .models import Reminder


def get_upcoming_reminders(user):
    return Reminder.objects.filter(user=user, due_time__gt=now()).order_by('due_time')


def mark_task_complete(reminder):
    reminder.completed = True
    reminder.save()


def filter_reminders_by_priority(user, priority):
    return Reminder.objects.filter(user=user, priority=priority)