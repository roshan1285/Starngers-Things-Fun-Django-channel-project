from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Friends
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync 

@receiver( post_save , sender=Friends)
def send_radio_update(sender,instance,created ,**kwargs):
    channel_layer = get_channel_layer()

    if created and instance.status == 1:
        target_group = f"user_{instance.receiver.id}_radio"
        data = {
            'type': 'incoming_request',
            'sender_id': instance.sender.id,
            'sender_name': instance.sender.username,
            'frequency' : instance.frequency,
        }
        async_to_sync(channel_layer.group_send)(
            target_group, {'type': 'radio_signal', 'data': data}
        )

    # CASE 2: Accepted (Status 2) -> Notify Sender
    elif instance.status == 2:
        request_target_group = f"user_{instance.sender.id}_radio"
        accepter_target_group = f"user_{instance.receiver.id}_radio"

        requester_data = {
            'type': 'request_accepted',
            'accepter_id': instance.receiver.id,
            'accepter_name': instance.receiver.username,
            'frequency' : instance.frequency,
        }
        accepter_data = {
            'type': 'request_accepted',
            'requester_id': instance.sender.id,
            'requester_name': instance.sender.username,
            'frequency' : instance.frequency,
        }

        async_to_sync(channel_layer.group_send)(
            request_target_group, {'type': 'radio_signal', 'data': requester_data}
        )
        async_to_sync(channel_layer.group_send)(
            accepter_target_group, {'type': 'radio_signal', 'data': accepter_data}
        )

    
    # CASE 3: Rejected (Status 3) -> Notify Sender
    elif instance.status == 3:
        request_target_group = f"user_{instance.sender.id}_radio"
        rejector_target_group = f"user_{instance.receiver.id}_radio"

        requester_data = {
            'type': 'request_rejected',
            'rejecter_id': instance.receiver.id,
            'frequency' : instance.frequency,
        }
        rejector_data = {
            'type': 'request_rejected',
            'requester_id': instance.sender.id,
            'frequency' : instance.frequency,
        }

        async_to_sync(channel_layer.group_send)(
            request_target_group, {'type': 'radio_signal', 'data': requester_data}
        )
        async_to_sync(channel_layer.group_send)(
            rejector_target_group, {'type': 'radio_signal', 'data': rejector_data}
        )


