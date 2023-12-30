# -*- coding: utf-8 -*-
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status

import hmac
import hashlib
from django.conf import settings 

from .tasks import process_webhook_event

@api_view(['POST'])
@permission_classes([AllowAny])
def easypost_webhook_callback(request):
    """
    Handle webhook callbacks from EasyPost with HMAC validation
    """

    if request.method == 'POST':
        # Extract relevant headers and data from the request
        webhook_signature = request.headers.get('HTTP_X_EASYPOST_HMAC_SHA256', '')
        post_content = request.body

        # Calculate the expected HMAC using the EasyPost secret key
        secret_key = settings.EASYPOST_WH_SECRET  # Use your EasyPost secret key from Django settings
        expected_signature = hmac.new(
            secret_key.encode('utf-8'),
            post_content,
            hashlib.sha256
        ).hexdigest()

        # Compare the calculated HMAC with the one provided in the request
        if hmac.compare_digest(webhook_signature, expected_signature):
            process_webhook_event.delay(request.body)
            return Response(status=status.HTTP_200_OK)
        else:
            # HMAC validation failed
            return Response({'detail': 'HMAC validation failed'}, status=status.HTTP_401_UNAUTHORIZED)

    return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
