from rest_framework import serializers
from django.db import models
from django.contrib.auth.models import User
from .models import Friends

from django.db.models import Q, F, Count

class UserSearchSerializer(serializers.ModelSerializer):
    friendship_status = serializers.SerializerMethodField()
    friend_count = serializers.SerializerMethodField()
    frequency = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'friendship_status', 'friend_count', 'frequency']

    def get_friendship_status(self, obj):
        request_user = self.context.get('request').user
        
        if obj == request_user:
            return 4 # Self

        # Check for relationship
        # Note: Using 'sender' because you updated your model
        friendship = Friends.objects.filter(
            (Q(sender=request_user, receiver=obj) | 
             Q(sender=obj, receiver=request_user))
        ).first()

        if not friendship:
            return 0 # Stranger (No Signal)
        
        current_status = int(friendship.status)
        # LOGIC FOR PENDING REQUESTS
        if current_status == 1: 
            # If YOU sent the request
            if friendship.sender == request_user:
                return 1 # "Tuning..." (Yellow Button)
            # If THEY sent the request
            else:
                return 5 # "INCOMING!" (Green Accept Button)
        
        # If Accepted (2) or Rejected (3)
        return current_status 


    def get_friend_count(self, obj):
        # Change 'accepted' to 2
        return Friends.objects.filter(
            (Q(sender=obj) | Q(receiver=obj)) & Q(status=2)
        ).count()
    
    def get_frequency(self, obj):
        request_user = self.context.get('request').user
        
        # Check for friendship
        friendship = Friends.objects.filter(
            (Q(sender=request_user, receiver=obj) | 
             Q(sender=obj, receiver=request_user))
        ).first()

        # Logic: Only show Frequency if Accepted (Status 2)
        # If pending or stranger, return a placeholder like "---"
        if friendship and friendship.status == "2" and friendship.frequency:
            print(f"there is the frequency, from {request_user.username}, {friendship.frequency} ")
            return friendship.frequency
        
        return "00.0" # Default static for strangers
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username']

class FriendSerializer(serializers.ModelSerializer):
    # We use the UserSerializer inside here to get full details
    sender = UserSerializer(read_only=True)
    receiver = UserSerializer(read_only=True)

    class Meta:
        model = "Friends"
        fields = ['id', 'sender', 'receiver', 'status', 'timestamp']