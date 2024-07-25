import json
import requests
from django.utils import timezone
from authentication.serializers import AzamPayAuthSerializer
from user_data.azam_pay_urls import AzamPayUrls
from authentication.models import AzamPayAuthToken
import logging

class Authentication:
    def __init__(self, client_id, client_secret, app_name):
        self.client_id = client_id
        self.client_secret = client_secret
        self.app_name = app_name

    def get_token(self):
        # Check if the token is still valid
        try:
            token_model = AzamPayAuthToken.objects.all().latest("created_at")  # Get the latest token
        except AzamPayAuthToken.DoesNotExist:
            token_model = None

        if token_model and token_model.expires_in > timezone.now():
            return token_model.access_token.strip()
        else:
            azamEnvurl = AzamPayUrls()
            url = azamEnvurl.getTokeUrl()
            pl = {
                "appName": self.app_name,
                "clientId": self.client_id,
                "clientSecret": self.client_secret,
            }
            payload = json.dumps(pl)
            headers = {"Content-Type": "application/json"}
            response = requests.post(url, headers=headers, data=payload)
            response_data = response.json()

            token = response_data["data"].get("accessToken")
            data = {
                'access_token': token,
                'refresh_token': response_data["data"].get("refreshToken"),
                'token_type': response_data["data"].get("tokenType", "Bearer"),
                'expires_in': response_data["data"].get("expire"),
            }

            # Create or update the token
            serializer = AzamPayAuthSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
            else:
                logging.error(f"Token serialization error: {serializer.errors}")

            return token