from rest_framework import serializers
from .models import Reminder

class ReminderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reminder
        fields = ['id', 'title', 'description', 'due_time', 'priority', 'category', 'completed', 'recurring', 'created_at']
        read_only_fields = ['id', 'created_at', 'user']  # ✅ Ensure 'user' is read-only
