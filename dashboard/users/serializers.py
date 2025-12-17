from rest_framework import serializers
from django.contrib.auth.models import User
from .models import UserPreference


class UserPreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserPreference
        fields = [
            'output_format', 'audio_quality', 'auto_process',
            'email_notifications', 'created_at', 'updated_at'
        ]


class UserSerializer(serializers.ModelSerializer):
    preferences = UserPreferenceSerializer(read_only=True)
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'full_name', 'date_joined', 'last_login', 'is_active', 'preferences'
        ]
        read_only_fields = ['id', 'date_joined', 'last_login', 'full_name']

    def get_full_name(self, obj):
        return obj.get_full_name() or obj.username