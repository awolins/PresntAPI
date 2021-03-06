import ipdb
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
from rest_auth.views import LoginView
from rest_auth.registration.views import RegisterView
from presnt_api.serializers import (
        UserSerializer,
        CourseSerializer,
        SectionSerializer,
        AttendanceSerializer,
    )
from presnt_api.models import (
        UserProfile,
        Course,
        Section,
        Attendance,
    )

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

class CourseViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    queryset = Course.objects.all().order_by('course_name')
    serializer_class = CourseSerializer
    filter_backends = (filters.DjangoFilterBackend, filters.OrderingFilter)
    filter_fields = ('id', 'course_name', 'semester')

class SectionViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    queryset = Section.objects.all().order_by('course')
    serializer_class = SectionSerializer
    filter_backends = (filters.DjangoFilterBackend, filters.OrderingFilter)
    filter_fields = ('id', 'course')

    @list_route()
    def get_sections(self, request):
        sections = Section.objects.filter(professor=request.user).order_by('-class_time')
        serializer = self.get_serializer(sections, many=True)
        return Response(serializer.data)

    @list_route(methods=['POST'])
    def register(self, request):
        section = Section.objects.get(access_code=request.data['access_code'])
        section.roster.add(request.user.pk)
        serializer = self.get_serializer(section)
        return Response(serializer.data)

    @list_route()
    def get_sections_student(self, request):
        sections = Section.objects.filter(roster__id__exact=request.user.pk).order_by('-class_time')
        serializer = self.get_serializer(sections, many=True)
        return Response(serializer.data)

class AttendanceViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    queryset = Attendance.objects.all().order_by('section')
    serializer_class = AttendanceSerializer

class CustomLoginView(LoginView):

    def get_response(self):
       response = super(CustomLoginView, self).get_response()
       user_profile = UserProfile.objects.get(user__pk=self.user.pk)
       response.data.update({'user' : str(self.user.pk), 'prof': user_profile.is_professor})
       return response

class CustomRegistrationView(RegisterView):

    def create(self, request, *args, **kwargs):
       response = super(CustomRegistrationView, self).create(request)
       new_user = User.objects.get(username=request.data['username'])
       new_user_profile = UserProfile.objects.get(user=new_user)
       response.data.update({'user' : new_user.pk, 'prof': new_user_profile.is_professor })
       return response

