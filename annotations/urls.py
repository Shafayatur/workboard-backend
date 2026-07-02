from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import ImageViewSet, ShapeViewSet

router = DefaultRouter()
router.register('images', ImageViewSet, basename='image')
router.register('shapes', ShapeViewSet, basename='shape')

urlpatterns = [
    # nested route: shapes scoped to one image
    path('images/<int:image_pk>/shapes/',
         ShapeViewSet.as_view({'get': 'list', 'post': 'create'}),
         name='image-shapes'),
] + router.urls
