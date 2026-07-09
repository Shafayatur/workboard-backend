from rest_framework import status, viewsets
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from config.gemini_client import GeminiError, call_gemini
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


class SuggestLabelView(APIView):
    """
    POST {image_base64} -> {label}

    Given a cropped PNG (base64) of a just-drawn polygon region, asks
    Gemini's vision model for a short label — used to auto-name shapes
    instead of leaving them as "Region 01".
    """

    def post(self, request):
        image_base64 = (request.data.get('image_base64') or '').strip()
        if not image_base64:
            return Response(
                {'detail': 'image_base64 is required'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Strip a data URL prefix like "data:image/png;base64," if present.
        if image_base64.startswith('data:') and ',' in image_base64:
            image_base64 = image_base64.split(',', 1)[1]

        prompt = (
            "Look at this cropped image region and respond with a short, "
            "specific 2-5 word label describing what it shows. Respond with "
            "only the label text — no punctuation, no quotes, no explanation."
        )
        try:
            raw = call_gemini([
                {'text': prompt},
                {'inline_data': {'mime_type': 'image/png', 'data': image_base64}},
            ])
        except GeminiError as exc:
            return Response(
                {'detail': f'Could not label shape: {exc}'},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        label = raw.strip().strip('"').strip("'")
        label = ' '.join(label.split()[:6])  # keep it short and sane
        return Response({'label': label})