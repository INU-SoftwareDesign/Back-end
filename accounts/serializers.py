from rest_framework import serializers
from .models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'role', 'name', 'email', 'phone']
        read_only_fields = ['id', 'username', 'role']
