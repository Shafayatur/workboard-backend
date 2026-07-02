from rest_framework import viewsets
from rest_framework.parsers import FormParser, MultiPartParser

from .models import Image, Shape
from .serializers import ImageSerializer, ShapeSerializer


class ImageViewSet(viewsets.ModelViewSet):
    serializer_class = ImageSerializer
    parser_classes = [MultiPartParser, FormParser]

    def get_queryset(self):
        return Image.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class ShapeViewSet(viewsets.ModelViewSet):
    """
    Nested under an image: /api/images/<image_pk>/shapes/
    Also supports direct delete via /api/shapes/<pk>/ (see urls).
    """
    serializer_class = ShapeSerializer

    def get_queryset(self):
        qs = Shape.objects.filter(image__owner=self.request.user)
        image_pk = self.kwargs.get('image_pk')
        if image_pk:
            qs = qs.filter(image_id=image_pk)
        return qs

    def perform_create(self, serializer):
        image_pk = self.kwargs['image_pk']
        image = Image.objects.get(pk=image_pk, owner=self.request.user)
        serializer.save(image=image)
