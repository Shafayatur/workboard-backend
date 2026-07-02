from rest_framework.routers import DefaultRouter

from .views import TagViewSet, TaskViewSet

router = DefaultRouter()
router.register('tasks', TaskViewSet, basename='task')
router.register('tags', TagViewSet, basename='tag')

urlpatterns = router.urls
