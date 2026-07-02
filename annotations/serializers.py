from rest_framework import serializers

from .models import Image, Shape


class ShapeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shape
        fields = ['id', 'points', 'label', 'color', 'created_at']
        read_only_fields = ['id', 'created_at']


class ImageSerializer(serializers.ModelSerializer):
    shapes = ShapeSerializer(many=True, read_only=True)

    class Meta:
        model = Image
        fields = ['id', 'file', 'name', 'order', 'uploaded_at', 'shapes']
        read_only_fields = ['id', 'uploaded_at']

    def create(self, validated_data):
        validated_data['owner'] = self.context['request'].user
        return super().create(validated_data)
