from datetime import date

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from config.gemini_client import GeminiError, call_gemini, extract_json
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


class ParseTaskView(APIView):
    """
    POST {text, today} -> {title, due_date, priority}

    Turns a free-text task description ("submit report by friday, high
    priority") into structured fields via Gemini, so the frontend can
    create a task from one line of natural language instead of a form.
    """

    def post(self, request):
        text = (request.data.get('text') or '').strip()
        today_str = request.data.get('today') or date.today().isoformat()

        if not text:
            return Response({'detail': 'text is required'}, status=status.HTTP_400_BAD_REQUEST)

        prompt = f"""You turn a short task description into structured JSON for a to-do app.
Today's date is {today_str} (YYYY-MM-DD). Use it to resolve relative dates like "tomorrow", "friday", or "next week".

Task description: "{text}"

Respond with ONLY a JSON object, no markdown, no explanation, in exactly this shape:
{{"title": "short clear task title", "due_date": "YYYY-MM-DD", "priority": "low" or "medium" or "high"}}

Rules:
- If no date is mentioned, use today's date: {today_str}.
- If no priority is implied, use "medium".
- The title should not repeat the date or priority words themselves.
"""
        try:
            raw = call_gemini([{'text': prompt}])
            parsed = extract_json(raw)
        except (GeminiError, ValueError) as exc:
            return Response(
                {'detail': f'Could not parse task: {exc}'},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        title = str(parsed.get('title', '')).strip() or text[:200]
        due_date = parsed.get('due_date') or today_str
        priority = parsed.get('priority')
        if priority not in ('low', 'medium', 'high'):
            priority = 'medium'

        return Response({'title': title, 'due_date': due_date, 'priority': priority})