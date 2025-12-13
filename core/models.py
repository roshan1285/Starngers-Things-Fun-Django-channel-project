from rest_framework import serializers
from django.db import models
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username']

class FriendSerializer(serializers.ModelSerializer):
    # We use the UserSerializer inside here to get full details
    request_sender = UserSerializer(read_only=True)
    receiver = UserSerializer(read_only=True)

    class Meta:
        model = "Friends"
        fields = ['id', 'sender', 'receiver', 'status', 'timestamp']

class Friends(models.Model):
    STATUS_CHOICES = (
        (1, 'Pending'),
        (2, 'Accepted'),
        (3, 'Rejected'),
    )
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_requests')
    # Who received the request
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_requests')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=1)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Ensure user can't send multiple requests to the same person
        unique_together = ('sender', 'receiver')

    def __str__(self):
        return f"{self.sender} -> {self.receiver} : {self.status}"


