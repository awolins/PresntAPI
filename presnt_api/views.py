from rest_framework import status, viewsets, filters
from rest_framework.decorators import api_view, list_route, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework.decorators import detail_route
from rest_framework import mixins
from django.contrib.auth.models import User, Group
from django.views.generic import RedirectView
from django.core import serializers
from presnt_api.serializers import UserSerializer
from presnt_api.models import UserProfile

@api_view(['GET'])
def get_ocr_view(request):
    return Response({})


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    permission_classes = (IsAuthenticated,)
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    filter_backends = (filters.DjangoFilterBackend, filters.OrderingFilter)
    filter_fields = ('id', 'username', 'email')
    model = User

    @list_route(methods=['POST'])
    def login(self, request):
        """
        User login/ Aquire token
        ---
        omit_serializer: true
        parameters:
            - name: username
              type: string
            - name: password
              type: string
        """
        serializer = AuthTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token':token.key,
            'user_id': User.objects.get(username=str(user)).pk
            })
