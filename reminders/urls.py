from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import ReminderViewSet, delete_past_reminders

router = DefaultRouter()
router.register(r'reminders', ReminderViewSet, basename='reminder')

urlpatterns = router.urls

urlpatterns += [
    path('delete_past/', delete_past_reminders, name='delete_past_reminders'),
]
