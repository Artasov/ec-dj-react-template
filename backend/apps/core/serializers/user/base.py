from adrf.serializers import (
    Serializer as ASerializer
)
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from apps.core.models.user import User
from utils.aserializers import AModelSerializer


class UserUsernameSerializer(ASerializer):
    username = serializers.CharField(min_length=2)


class UserSelfSerializer(AModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'phone', 'birth_date', 'date_joined',
                  'first_name', 'last_name', 'middle_name',
                  'avatar', 'is_staff', 'email')


class UserUpdateSerializer(AModelSerializer):
    class Meta:
        model = User
        fields = [
            'username', 'first_name', 'last_name', 'middle_name',
            'phone', 'birth_date', 'date_joined'
        ]
        read_only_fields = ['date_joined']


class UserAvatarSerializer(AModelSerializer):
    class Meta:
        model = User
        fields = ['avatar']

    def update(self, instance, validated_data):
        instance.avatar = validated_data.get('avatar', instance.avatar)
        instance.save()
        return instance


class UserPublicSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'avatar', 'first_name', 'last_name')


class SignUpSerializer(ASerializer):
    username = serializers.CharField(required=True, )
    email = serializers.EmailField(required=True, )
    password = serializers.CharField(required=True, )
