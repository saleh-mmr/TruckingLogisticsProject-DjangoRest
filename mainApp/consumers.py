from channels.generic.websocket import WebsocketConsumer
import json
from asgiref.sync import async_to_sync
from mainApp import serializers
from mainApp import models
from rest_framework.renderers import JSONRenderer
from rest_framework.authtoken.models import Token
from mainApp import Authentication


class ChatConsumer(WebsocketConsumer):
    def new_message(self, data):
        message = data.get("message", None)
        message_model = models.Message.objects.create(sender=self.user, receiver=self.interlocutor, request=self.request,
                                                      content=message)
        result = json.loads(self.message_serializer(message_model, False).decode('utf-8'))['content']
        self.sent_to_chat_message(result)

    def fetch_message(self, data):
        qs = models.Message.last_message(self, self.user, self.interlocutor, self.request)
        message_json = self.message_serializer(qs, True)
        message_json = message_json.decode('utf-8').replace('false', 'False')
        message_json = message_json.replace('true', 'True')
        content = {
            "message": eval(message_json)
        }
        self.chat_message(content)

    def message_serializer(self, qs, flag):
        serialized_message = serializers.MessageSerializers(qs, many=flag)
        content = JSONRenderer().render(serialized_message.data)
        return content

    def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name
        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )
        token = ''
        for i in self.scope['headers']:
            if i[0].decode('utf-8') == 'token':
                token = Token.objects.get(key=i[1].decode('utf-8'))
        if not Authentication.is_token_expired(token):
            self.user = token.user
            if str(self.user) in str(self.room_name):
                temp_str = str(self.room_name)
                self.interlocutor = models.MyUser.objects.get(username=temp_str.replace(str(self.user), ''))
                self.request = models.Request.objects.get(id=int(self.scope['url_route']['kwargs']['request_id']))
                self.accept()

    commands = {
        "new_message": new_message,
        "fetch_message": fetch_message,
    }

    def disconnect(self, code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    def receive(self, text_data=None, bytes_data=None):
        text_data_dict = json.loads(text_data)
        command = text_data_dict['command']
        self.commands[command](self, text_data_dict)

    def sent_to_chat_message(self, message):
        # Send message to room group
        async_to_sync(self.channel_layer.group_send)(
            self.room_grou
        p_name,
            {
                'type': 'chat_message',
                'message': message
            }
        )

    # Receive message from room group
    def chat_message(self, event):
        message = event['message']
        # Send message to WebSocket
        self.send(text_data=json.dumps({
            'message': message
        }))
