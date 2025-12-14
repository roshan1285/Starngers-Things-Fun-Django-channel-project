from django.db import models
from django.contrib.auth.models import User
import random


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
    frequency = models.CharField(max_length=10, blank=True, null=True)

    class Meta:
        # Ensure user can't send multiple requests to the same person
        unique_together = ('sender', 'receiver')

    def save(self, *args, **kwargs):
        if not self.frequency:
            while True:
                new_freq = f"{random.uniform(88.0, 108.0):.1f}"
                if not Friends.objects.filter(frequency=new_freq).exists():
                    self.frequency = new_freq
                    break
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.sender} -> {self.receiver} : {self.status} [{self.frequency}]"


