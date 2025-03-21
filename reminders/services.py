from django.utils import timezone
from .models import Reminder
from datetime import timedelta
from dateutil.relativedelta import relativedelta
from collections import Counter


def get_upcoming_reminders(user):
    return Reminder.objects.filter(user=user, due_time__gt=timezone.now()).order_by('due_time')

def calculate_next_due(due_time, recurring):
    if recurring == 'daily':
        return due_time + timezone.timedelta(days=1)
    elif recurring == 'weekly':
        return due_time + timezone.timedelta(weeks=1)
    elif recurring == 'monthly':
        return due_time + relativedelta(months=1)
    elif recurring == 'yearly':
        return due_time + relativedelta(years=1)
    return due_time


def mark_task_complete(reminder):
    reminder.completed = True
    reminder.save()

    if reminder.recurring:
        next_due_time = calculate_next_due(reminder.due_time, reminder.recurring)

        Reminder.objects.create(
            user=reminder.user,
            title=reminder.title,
            description=reminder.description,
            due_time=next_due_time,
            priority=reminder.priority,
            category=reminder.category,
            recurring=reminder.recurring
        )
        return "Task marked as complete. New recurring reminder created."
    else:
        return "Task marked as complete."


def filter_reminders_by_priority(user, priority):
    print(f"Filtering reminders where priority='{priority}'")  # Debugging output

    # Ensure case-insensitive filtering
    reminders = Reminder.objects.filter(user=user, priority__iexact=priority)

    print(f"Filtered reminders (before return): {list(reminders.values('id', 'priority'))}")  # Debugging output

    return reminders  # <-- Ensure returning the queryset instead of an undefined variable


def get_reminder_summary(user):
    from .models import Reminder

    reminders = Reminder.objects.filter(user=user)

    summary = {
        "total_reminders": reminders.count(),
        "status": {
            "completed": reminders.filter(completed=True).count(),
            "uncompleted": reminders.filter(completed=False).count(),
            "overdue": reminders.filter(due_time__lt=timezone.now(), completed=False).count(),
            "upcoming": reminders.filter(due_time__gt=timezone.now(), completed=False).count(),
        },
        "priority_distribution": dict(Counter(reminders.values_list('priority', flat=True))),
        "category_distribution": dict(Counter(reminders.values_list('category', flat=True))),
    }

    return summary

def get_due_soon_reminders(user, within_minutes=60):
    from django.utils import timezone
    from datetime import timedelta

    now = timezone.now()
    cutoff = now + timedelta(minutes=within_minutes)

    return Reminder.objects.filter(
        user=user,
        completed=False,
        due_time__gte=now,
        due_time__lte=cutoff
    ).order_by('due_time')
