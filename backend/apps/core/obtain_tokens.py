from adrf.decorators import api_view
from asgiref.sync import sync_to_async
from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework.decorators import permission_classes
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from apps.core.models.user import User


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        # Get the user by email or username
        user = None
        username = None
        username_or_email = attrs.get('username', None)
        password = attrs.get('password')

        if '@' in username_or_email:
            try:
                user = User.objects.get(email=username_or_email)
            except User.DoesNotExist:
                try:
                    user = User.objects.get(username=username_or_email)
                except User.DoesNotExist:
                    pass
            username = user.username
        else:
            username = username_or_email

        if username:
            user = authenticate(username=username, password=password)
            if not user:
                raise AuthenticationFailed('Invalid user or password')
            return super().validate({
                'username': user.username,
                'password': password
            })

        else:
            raise AuthenticationFailed('User is not found')


@api_view(('POST',))
@permission_classes((AllowAny,))
async def custom_token_obtain_pair_view(request):
    serializer = CustomTokenObtainPairSerializer(data=request.data)
    await sync_to_async(serializer.is_valid, thread_sensitive=True)(raise_exception=True)
    return Response(serializer.validated_data, status=status.HTTP_200_OK)
