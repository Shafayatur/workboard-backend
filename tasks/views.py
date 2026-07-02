from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Tag, Task
from .serializers import TagSerializer, TaskSerializer


class TagViewSet(viewsets.ModelViewSet):
    serializer_class = TagSerializer

    def get_queryset(self):
        return Tag.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class TaskViewSet(viewsets.ModelViewSet):
    serializer_class = TaskSerializer

    def get_queryset(self):
        qs = Task.objects.filter(owner=self.request.user)
        date = self.request.query_params.get('date')
        if date:
            qs = qs.filter(due_date=date)
        return qs

    @action(detail=True, methods=['patch'])
    def reorder(self, request, pk=None):
        """Update status/order after a drag-and-drop move."""
        task = self.get_object()
        status_value = request.data.get('status')
        order = request.data.get('order')
        if status_value is not None:
            task.status = status_value
        if order is not None:
            task.order = order
        task.save(update_fields=['status', 'order', 'updated_at'])
        return Response(TaskSerializer(task).data)
