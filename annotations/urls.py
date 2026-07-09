from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import ImageViewSet, ShapeViewSet, SuggestLabelView

router = DefaultRouter()
router.register('images', ImageViewSet, basename='image')
router.register('shapes', ShapeViewSet, basename='shape')

urlpatterns = [
    path('images/<int:image_pk>/shapes/',
         ShapeViewSet.as_view({'get': 'list', 'post': 'create'}),
         name='image-shapes'),
    path('annotate/suggest-label/', SuggestLabelView.as_view(), name='suggest-label'),
] + router.urls