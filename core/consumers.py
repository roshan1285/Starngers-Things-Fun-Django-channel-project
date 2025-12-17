import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.core.cache import cache 

class RadioConsumer(AsyncWebsocketConsumer):
    async def connect(self):

        self.user = self.scope["user"]

        if self.user.is_anonymous:
            await self.close()
        else:
            self.room_group_name = f"user_{self.user.id}_radio"
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )
            await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def radio_signal(self,event):
        await self.send(text_data=json.dumps(event['data']))
        
class CommsConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Get the frequency from the URL (e.g., "94.3")
        self.room_name = self.scope['url_route']['kwargs']['frequency']
        self.room_group_name = f'comms_{self.room_name}'
        self.user = self.scope["user"]

        # Join the frequency group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):

        freq = self.room_name
        user_id = self.user.id
        
        hawkins_key = f'presence_{freq}_hawkins'
        if cache.get(hawkins_key) == user_id:
            cache.delete(hawkins_key) # Erase name
            print(f"USER {self.user.username} checked out of Hawkins")

        # Check Upside Down Key
        upside_key = f'presence_{freq}_upsidedown'
        if cache.get(upside_key) == user_id:
            cache.delete(upside_key) # Erase name
            print(f"USER {self.user.username} checked out of Upside Down")

        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive signal from Browser (User pressed a key)
    async def receive(self, text_data):
        data = json.loads(text_data)

        if data.get('type') == 'join_dimension':
                theme = data.get('theme') # 'hawkins' or 'upsidedown'

                cache_key = f'presence_{self.room_name}_{theme}'
                cache.set(cache_key, self.user.id, timeout=3600)

                # Optional: Print to console so you can see it working
                print(f"USER {self.user.username} checked into {theme}")

        if data.get('action'):
            # Broadcast it to everyone on this frequency
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'light_signal',
                    'key': data['key'],
                    'action': data['action'], # 'down' or 'up'
                    'sender_id': self.scope["user"].id,
                    'from': data['from']
                }
            )

    # Send signal back to Browser (Light it up!)
    async def light_signal(self, event):
        # We send the data to the frontend so JS can light the bulb
        await self.send(text_data=json.dumps(event))