from rest_framework import serializers
from django.contrib.auth.models import User


class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'full_name', 'date_joined', 'last_login', 'is_active'
        ]
        read_only_fields = ['id', 'date_joined', 'last_login', 'full_name']

    def get_full_name(self, obj):
        return obj.get_full_name() or obj.username
            instance.avatar = avatar

        return super().update(instance, validated_data)