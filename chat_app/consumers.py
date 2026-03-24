import json
from channels.generic.websocket import AsyncWebsocketConsumer
from .db_utils import ChatManager

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = "global_chat"
        self.room_group_name = f"chat_{self.room_name}"
        self.chat_manager = ChatManager()

        # Rejoindre le groupe de discussion dans Redis
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()
        print(f"Connexion WebSocket acceptée pour {self.channel_name}")

    async def disconnect(self, close_code):
        # Quitter le groupe Redis
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Recevoir un message depuis le WebSocket (du navigateur)
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        sender = text_data_json.get('sender', 'Anonyme')

        # 1. Sauvegarder dans MongoDB via ton ChatManager
        self.chat_manager.send_message(sender, message)

        # 2. Envoyer le message au groupe Redis pour diffusion
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'sender': sender
            }
        )

    # Recevoir le message depuis le groupe Redis (diffusion)
    async def chat_message(self, event):
        message = event['message']
        sender = event['sender']

        # Envoyer le message au navigateur (WebSocket)
        await self.send(text_data=json.dumps({
            'text': message,
            'sender': sender
        }))