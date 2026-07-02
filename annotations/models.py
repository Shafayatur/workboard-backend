from django.conf import settings
from django.db import models


class Image(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='images')
    file = models.ImageField(upload_to='annotate_images/')
    name = models.CharField(max_length=200, blank=True)
    order = models.PositiveIntegerField(default=0)  # position in the slider/strip
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', 'uploaded_at']

    def __str__(self):
        return self.name or f'Image {self.id}'


class Shape(models.Model):
    image = models.ForeignKey(Image, on_delete=models.CASCADE, related_name='shapes')
    # Polygon vertices, normalized 0-1 relative to image width/height so they
    # stay correct regardless of the rendered canvas size.
    points = models.JSONField()
    label = models.CharField(max_length=100, blank=True)
    color = models.CharField(max_length=7, default='#D6402A')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.label or f'Shape {self.id} on {self.image_id}'
