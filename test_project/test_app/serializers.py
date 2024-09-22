from rest_framework import serializers
from .models import User, Organization, Role, Member

# User Serializer
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'password', 'profile', 'status', 'settings']
        extra_kwargs = {
            'password': {'write_only': True}
        }
    def create(self, validated_data):
        # Use set_password to hash the password
        user = User(**validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user

    def update(self, instance, validated_data):
        # Update other fields if necessary
        instance.email = validated_data.get('email', instance.email)
        # Only hash the password if it's being updated
        if 'password' in validated_data:
            instance.set_password(validated_data['password'])
        instance.save()
        return instance
# Organization Serializer
class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = ['name', 'status', 'personal', 'settings']

# Role Serializer
class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ['name', 'description', 'org']

# Member Serializer
class MemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = Member
        fields = ['user', 'org', 'role', 'status', 'settings']
