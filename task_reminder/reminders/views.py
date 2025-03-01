from rest_framework import viewsets, filters, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Reminder
from rest_framework.authentication import TokenAuthentication
from .serializers import ReminderSerializer
from rest_framework.permissions import IsAuthenticated
from .services import get_upcoming_reminders, mark_task_complete, filter_reminders_by_priority

class ReminderViewSet(viewsets.ModelViewSet):
    queryset = Reminder.objects.all()
    serializer_class = ReminderSerializer
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['due_time', 'priority']
    permission_classes = [IsAuthenticated]  # ✅ Require authentication
    authentication_classes = [TokenAuthentication]

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Reminder.objects.none()  # ✅ Avoid TypeError
        return self.queryset.filter(user=self.request.user)

    @action(detail=False, methods=['get'])
    def list_reminders(self, request):
        priority = request.query_params.get('priority')
        reminders = filter_reminders_by_priority(request.user, priority) if priority else self.get_queryset()
        return Response(ReminderSerializer(reminders, many=True).data)

    @action(detail=False, methods=['get'])
    def upcoming_reminders(self, request):
        reminders = get_upcoming_reminders(request.user)
        return Response(ReminderSerializer(reminders, many=True).data)

    @action(detail=True, methods=['post'])
    def complete_task(self, request, pk=None):
        reminder = self.get_object()
        mark_task_complete(reminder)
        return Response({"message": "Task marked as complete"}, status=status.HTTP_200_OK)