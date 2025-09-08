import json
import requests
from django.utils import timezone
from authentication.serializers import AzamPayAuthSerializer
from user_data.azam_pay_urls import AzamPayUrls
from authentication.models import AzamPayAuthToken
from django.core.exceptions import ValidationError
from requests.exceptions import RequestException, Timeout, ConnectionError
import logging
from datetime import timedelta

class Authentication:
    def __init__(self, client_id, client_secret, app_name):
        if not all([client_id, client_secret, app_name]):
            raise ValueError("All authentication parameters are required")
        self.client_id = client_id
        self.client_secret = client_secret
        self.app_name = app_name
        self.logger = logging.getLogger(__name__)

    def get_token(self):
        """Get a valid access token, refreshing if necessary"""
        try:
            # Check if we have a valid token
            token_model = self._get_latest_token()
            
            if token_model and self._is_token_valid(token_model):
                self.logger.info("Using existing valid token")
                return token_model.access_token.strip()
            
            # Token is expired or doesn't exist, get a new one
            return self._fetch_new_token()
            
        except Exception as e:
            self.logger.error(f"Error getting token: {str(e)}")
            raise Exception(f"Authentication failed: {str(e)}")
    
    def _get_latest_token(self):
        """Get the latest token from database"""
        try:
            return AzamPayAuthToken.objects.all().latest("created_at")
        except AzamPayAuthToken.DoesNotExist:
            return None
    
    def _is_token_valid(self, token_model):
        """Check if token is still valid (with 5 minute buffer)"""
        if not token_model or not token_model.expires_in:
            return False
        
        # Add 5 minute buffer to avoid token expiry during request
        buffer_time = timezone.now() + timedelta(minutes=5)
        return token_model.expires_in > buffer_time
    
    def _fetch_new_token(self):
        """Fetch a new token from Azam Pay API"""
        try:
            azam_urls = AzamPayUrls()
            url = azam_urls.getTokeUrl()
            
            payload = {
                "appName": self.app_name,
                "clientId": self.client_id,
                "clientSecret": self.client_secret,
            }
            
            headers = {
                "Content-Type": "application/json",
                "User-Agent": "Vista-Backend/1.0"
            }
            
            self.logger.info("Requesting new token from Azam Pay")
            
            response = requests.post(
                url, 
                headers=headers, 
                data=json.dumps(payload)
                # No timeout for sandbox - allows longer response times
            )
            
            # Check if request was successful
            response.raise_for_status()
            
            response_data = response.json()
            
            # Validate response structure
            if not response_data.get("success", False):
                error_msg = response_data.get("message", "Unknown error")
                raise Exception(f"Azam Pay API error: {error_msg}")
            
            if "data" not in response_data:
                raise Exception("Invalid response format from Azam Pay")
            
            data = response_data["data"]
            token = data.get("accessToken")
            
            if not token:
                raise Exception("No access token received from Azam Pay")
            
            # Save token to database
            token_data = {
                'access_token': token,
                'refresh_token': data.get("refreshToken"),
                'token_type': data.get("tokenType", "Bearer"),
                'expires_in': data.get("expire"),
            }
            
            serializer = AzamPayAuthSerializer(data=token_data)
            if serializer.is_valid():
                serializer.save()
                self.logger.info("New token saved successfully")
            else:
                self.logger.error(f"Token serialization error: {serializer.errors}")
                raise Exception(f"Failed to save token: {serializer.errors}")
            
            return token
            
        except RequestException as e:
            self.logger.error(f"Network error while fetching token: {str(e)}")
            raise Exception(f"Network error: {str(e)}")
        except json.JSONDecodeError as e:
            self.logger.error(f"Invalid JSON response from Azam Pay: {str(e)}")
            raise Exception("Invalid response from payment gateway")
        except KeyError as e:
            self.logger.error(f"Missing key in Azam Pay response: {str(e)}")
            raise Exception(f"Invalid response format: missing {str(e)}")