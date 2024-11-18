import json
from mailbox import Message
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth.models import User
from asgiref.sync import sync_to_async

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['username']
        self.room_group_name = f"chat_{self.room_name}"

        # Join the room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave the room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data['message']
        sender = self.scope['user']
        receiver_username = data['receiver']
        
        # Save the message to the database
        receiver = await sync_to_async(User.objects.get)(username=receiver_username)
        msg = await sync_to_async(Message.objects.create)(sender=sender, receiver=receiver, text=message)

        # Send the message to the room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'sender': sender.username,
                'receiver': receiver.username,
                'timestamp': str(msg.timestamp),
                'read': 
msg.read

            }
        )

    async def chat_message(self, event):
        message = event['message']
        sender = event['sender']
        receiver = event['receiver']
        timestamp = event['timestamp']
        read = event['read']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'sender': sender,
            'receiver': receiver,
            'message': message,
            'timestamp': timestamp,
            'read': read
        })) 
