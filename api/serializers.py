from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate
from .models import Player, Mission, Puzzle, PuzzleSubmission

User = get_user_model()


class PlayerSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='player-detail')

    class Meta:
        model = Player
        fields = '__all__'


class MissionSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='mission-detail')

    class Meta:
        model = Mission
        fields = '__all__'


class PuzzleSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='puzzle-detail')

    class Meta:
        model = Puzzle
        fields = '__all__'
        extra_kwargs = {
            'mutation_data': {'write_only': True}
        }


class PuzzleSubmissionSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='submission-detail')

    class Meta:
        model = PuzzleSubmission
        fields = '__all__'


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=255)
    password = serializers.CharField(
        max_length=128,
        write_only=True,
        style={'input_type': 'password'}
    )

    def validate(self, data):
        username = data.get('username')
        password = data.get('password')

        if username and password:
            user = authenticate(username=username, password=password)
            if not user:
                raise serializers.ValidationError(
                    'Unable to log in with provided credentials.'
                )
        else:
            raise serializers.ValidationError(
                'Must include "username" and "password".'
            )

        data['user'] = user
        return data


class RegisterSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    password = serializers.CharField(
        max_length=128,
        min_length=8,
        write_only=True,
        style={'input_type': 'password'}
    )

    def validate(self, data):
        if User.objects.filter(username=data['username']).exists():
            raise serializers.ValidationError("Username already exists.")
        if User.objects.filter(email=data['email']).exists():
            raise serializers.ValidationError("Email already exists.")
        return data

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user
