from rest_framework import serializers

from mainApp import models


class MessageSerializers(serializers.ModelSerializer):
    class Meta:
        model = models.Message
        fields = ['__str__', 'sender', 'receiver', 'request', 'content', 'timestamp', 'is_read']
