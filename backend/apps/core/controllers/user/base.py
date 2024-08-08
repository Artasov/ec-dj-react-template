from adrf.decorators import api_view
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_200_OK

from apps.core.exceptions.base import CoreExceptions
from apps.core.exceptions.user import UserExceptions
from apps.core.models import User
from apps.core.responses.success import Responses
from apps.core.serializers.user.base import UserSelfSerializer, UserUsernameSerializer, UserUpdateSerializer, \
    UserAvatarSerializer
from utils.base import acontroller


@acontroller('Get current user json info')
@api_view(('GET',))
@permission_classes((IsAuthenticated,))
async def current_user(request) -> Response:
    return Response(await UserSelfSerializer(request.user).adata, status=200)


@acontroller('Rename current user')
@api_view(('POST',))
@permission_classes((IsAuthenticated,))
async def rename_current_user(request) -> Response:
    serializer = UserUsernameSerializer(data=request.data)
    if serializer.is_valid():
        data = await serializer.adata
        username = data.get('username')
        if username == request.user.username: raise UserExceptions.AlreadyThisUsername()
        if await User.objects.filter(username=username).aexists(): raise UserExceptions.UsernameAlreadyExists()
        request.user.username = username
        await request.user.asave()
        return Responses.Success.RenameCurrentUser
    raise CoreExceptions.SerializerErrors(
        serializer_errors=serializer.errors,
        status_code=HTTP_400_BAD_REQUEST
    )


@acontroller('Update current user avatar')
@api_view(('PATCH',))
@permission_classes([IsAuthenticated])
async def update_avatar(request):
    user = request.user
    serializer = UserAvatarSerializer(user, data=request.data, partial=True)
    if await serializer.ais_valid():
        await serializer.asave()
        return Response(serializer.data, status=HTTP_200_OK)
    return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)


@acontroller('Update current user')
@api_view(('PATCH',))
@permission_classes((IsAuthenticated,))
async def update_user(request):
    user = request.user
    serializer = UserUpdateSerializer(user, data=request.data, partial=True)
    if await serializer.ais_valid():
        await serializer.asave()
        return Response(serializer.data, status=HTTP_200_OK)
    return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)


