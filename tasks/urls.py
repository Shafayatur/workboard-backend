from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import ParseTaskView, TagViewSet, TaskViewSet

router = DefaultRouter()
router.register('tasks', TaskViewSet, basename='task')
router.register('tags', TagViewSet, basename='tag')

urlpatterns = [
    # Must come before router.urls: otherwise the router's /tasks/<pk>/
    # pattern would greedily match "parse" as a pk value.
    path('tasks/parse/', ParseTaskView.as_view(), name='task-parse'),
] + router.urls