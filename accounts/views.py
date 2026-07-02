from rest_framework.generics import RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView

from .serializers import EmailTokenObtainPairSerializer, UserSerializer


class LoginView(TokenObtainPairView):
    """POST email + password -> access/refresh tokens + user info."""
    serializer_class = EmailTokenObtainPairSerializer


class MeView(RetrieveAPIView):
    """GET current authenticated user."""
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user
