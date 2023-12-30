# serializers.py
from rest_framework import serializers

class WebhookEventSerializer(serializers.Serializer):
    # Adjust fields based on the actual structure of your JSON data
    field1 = serializers.CharField()
    field2 = serializers.CharField()
    # Add other fields as needed
