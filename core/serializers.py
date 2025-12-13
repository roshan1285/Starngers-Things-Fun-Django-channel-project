from rest_framework import serializers
from django.db import models
from django.contrib.auth.models import User
from .models import Friends

from django.db.models import Q, F, Count

class UserSearchSerializer(serializers.ModelSerializer):
    # We add these two custom fields that aren't in the User database table
    friendship_status = serializers.SerializerMethodField()
    friend_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'friendship_status', 'friend_count']

    # Logic: Calculate the relationship between Request User and THIS User
    def get_friendship_status(self, obj):
        # 'obj' is the user we are looking at in the search result
        # 'request.user' is YOU (the person searching)
        request_user = self.context.get('request').user

        if obj == request_user:
            return 'self'

        # Check database for a link
        friendship = Friends.objects.filter(
            (Q(sender=request_user, receiver=obj) | 
             Q(sender=obj, receiver=request_user))
        ).first()

        if not friendship:
            return 'none' # Strangers
        
        # If pending, we need to know who sent it
        if friendship.status == 'pending':
            if friendship.sender == request_user:
                return 'sent' # You sent it
            return 'received' # They sent it to you
            
        return friendship.status # 'accepted' or 'rejected'

    # Logic: Count how many accepted friends this person has
    def get_friend_count(self, obj):
        return Friends.objects.filter(
            (Q(sender=obj) | Q(receiver=obj)) & Q(status='accepted')
        ).count()
    
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