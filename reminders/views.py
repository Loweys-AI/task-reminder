from rest_framework import viewsets, filters, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Reminder
from rest_framework.authentication import TokenAuthentication
from .serializers import ReminderSerializer
from rest_framework.permissions import IsAuthenticated
from .services import get_upcoming_reminders, mark_task_complete, filter_reminders_by_priority
from django.utils.timezone import now, timedelta
from .services import filter_reminders_by_priority
from .services import get_reminder_summary
from .services import get_due_soon_reminders
from reminders.models import Reminder
from rest_framework.decorators import api_view, permission_classes
from django.utils import timezone

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def completed_today(request):
    user = request.user
    today = timezone.now().date()
    reminders = Reminder.objects.filter(user=user, completed=True, due_time__date=today)
    serializer = ReminderSerializer(reminders, many=True)
    return Response({'count': reminders.count(), 'reminders': serializer.data})



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def completed_summary(request):
    user = request.user
    today = now().date()
    one_week_ago = today - timedelta(days=6)

    summary = {}
    for i in range(7):
        day = one_week_ago + timedelta(days=i)
        count = Reminder.objects.filter(user=user, completed=True, due_time__date=day).count()
        summary[str(day)] = count

    return Response({"weekly_completed_summary": summary})

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_past_reminders(request):
    print("✅ DELETE request received")  # Debugging log

    user = request.user
    past_reminders = Reminder.objects.filter(user=user, due_time__lt=now())

    if not past_reminders.exists():
        print("❌ No reminders found")  # Debugging log
        return Response({"message": "No past reminders found."}, status=404)

    count, _ = past_reminders.delete()
    print(f"✅ Deleted {count} reminders")  # Debugging log
    return Response({"message": f"Deleted {count} past reminders."}, status=200)
class ReminderViewSet(viewsets.ModelViewSet):
    queryset = Reminder.objects.all()
    serializer_class = ReminderSerializer
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['due_time', 'priority']
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    timeframe = now() + timedelta(minutes=45)
    due_soon_reminders = Reminder.objects.filter(due_time__lte=timeframe, due_time__gte=now())

    def get_queryset(self):
        queryset = Reminder.objects.filter(user=self.request.user)

        # ✅ Overdue filtering
        overdue = self.request.query_params.get('overdue')
        if overdue == 'true':
            queryset = queryset.filter(due_time__lt=now(), completed=False)

        # ✅ Priority filtering (combine with existing filter)
        priority = self.request.query_params.get('priority', '').strip().lower()
        if priority in ['high', 'medium', 'low']:
            queryset = queryset.filter(priority=priority)  # 👈 Apply filter to existing queryset

        return queryset
    # ✅ Ensure user-specific reminders

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)  # ✅ Assign authenticated user automatically

    @action(detail=False, methods=['get'], url_path='list')
    def list_reminders(self, request):
        priority = request.query_params.get('priority', '').strip().lower()


        if priority:
            priority = priority.strip().lower()
            print(f"Received priority param: {priority}")  # ✅ Debugging output
            reminders = filter_reminders_by_priority(request.user, priority)
        else:
            reminders = self.get_queryset()

        print(f"Final reminders sent: {list(reminders.values('id', 'priority'))}")  # ✅ Debugging output
        return Response(ReminderSerializer(reminders, many=True).data)

    @action(detail=False, methods=['get'])
    def upcoming_reminders(self, request):
        reminders = get_upcoming_reminders(request.user)
        return Response(ReminderSerializer(reminders, many=True).data)

    @action(detail=True, methods=['put', 'patch'], url_path='set_priority')
    def set_priority(self, request, pk=None):
        reminder = self.get_object()
        priority = request.data.get('priority')

        if priority not in ['high', 'medium', 'low']:
            return Response({'error': 'Invalid priority. Use high, medium, or low.'}, status=400)

        reminder.priority = priority
        reminder.save()
        return Response({'message': f"Priority updated to '{priority}'."}, status=200)


    @action(detail=True, methods=['post'])
    def complete_task(self, request, pk=None):
        reminder = self.get_object()
        message = mark_task_complete(reminder)
        return Response({"message": message}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path='summary')
    def reminder_summary(self, request):
        summary = get_reminder_summary(request.user)
        return Response(summary)

    @action(detail=False, methods=['get'])
    def due_soon(self, request):
        from rest_framework.exceptions import ValidationError

        try:
            minutes = int(request.query_params.get('minutes', 60))  # Default: 60 mins
            if minutes <= 0:
                raise ValidationError("Minutes must be a positive integer.")
        except ValueError:
            raise ValidationError("Invalid 'minutes' value. It must be an integer.")

        reminders = get_due_soon_reminders(request.user, within_minutes=minutes)
        serializer = self.get_serializer(reminders, many=True)
        return Response({
            "timeframe_minutes": minutes,
            "count": len(reminders),
            "reminders": serializer.data
        })



