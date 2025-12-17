from rest_framework import serializers
from .models import User, UserProfile


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = [
            'website', 'location', 'timezone',
            'articles_submitted', 'articles_processed'
        ]


class UserSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(read_only=True)
    full_name = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'full_name', 'avatar', 'bio', 'date_joined', 'last_login',
            'theme', 'notifications_enabled', 'profile'
        ]
        read_only_fields = ['id', 'date_joined', 'last_login', 'full_name']

    def update(self, instance, validated_data):
        # Handle avatar upload
        avatar = validated_data.pop('avatar', None)
        if avatar:
            instance.avatar = avatar

        return super().update(instance, validated_data)