from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import ReminderViewSet, delete_past_reminders, completed_today, completed_summary


router = DefaultRouter()
router.register(r'', ReminderViewSet, basename='reminder')  # no 'reminders/' prefix here

urlpatterns = router.urls

urlpatterns += [
    path('delete_past/', delete_past_reminders, name='delete_past_reminders'),
    path('reminders/completed_today/', completed_today, name='completed_today'),
    path('reminders/completed_summary/', completed_summary, name='completed_summary'),
]


