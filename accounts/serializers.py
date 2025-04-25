from rest_framework import serializers
from .models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'role', 'name', 'email', 'phone',
                  'birth_date', 'address', 'is_active', 'approval_status']
        read_only_fields = ['id', 'username', 'role']
