from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView

from apps.core.controllers.auth.common import signup, logout
from apps.core.controllers.user.base import (
    update_user, current_user, rename_current_user,
    update_avatar
)
from apps.core.obtain_tokens import custom_token_obtain_pair_view

urlpatterns = [
    path('token/', custom_token_obtain_pair_view, name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),

    path('signup/', signup, name='signup'),
    path('current_user/', current_user, name='current_user'),
    path('logout/', logout, name='logout'),

    path('user/rename/', rename_current_user, name='rename_current_user'),
    path('user/update/', update_user, name='update_user'),
    path('user/update/avatar/', update_avatar, name='update_avatar'),

]
