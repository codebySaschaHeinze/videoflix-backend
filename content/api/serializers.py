from django.contrib.auth import get_user_model
from rest_framework import serializers


User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    """Serializer for user registration."""

    confirmed_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['email', 'password', 'confirmed_password']
        extra_kwargs = {
            'password': {'write_only': True},
            'email': {'validators': []},
        }

    def validate(self, attrs):
        """Validate registration data."""
        if attrs['password'] != attrs['confirmed_password']:
            raise serializers.ValidationError(
                'Please check your input and try again.'
            )
        
        if User.objects.filter(email=attrs['email']).exists():
            raise serializers.ValidationError(
                'Please check your input and try again.'
            )
        
        return attrs
    
    def create(self, validated_data):
        """Create inactive user."""
        validated_data.pop('confirmed_password')
        return User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            is_active=False,
        )