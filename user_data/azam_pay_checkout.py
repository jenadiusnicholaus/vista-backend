from django.conf import settings
import requests
import json
import logging
from requests.exceptions import RequestException, Timeout, ConnectionError
from django.core.exceptions import ValidationError

from authentication.models import AzamPayAuthToken
from .azam_pay_urls import AzamPayUrls
from .azam_pay_auth import Authentication


class AzamPayCheckout:
    def __init__(self, accountNumber, amount, externalId, provider):
        # Validate input parameters
        if not all([accountNumber, amount, externalId, provider]):
            raise ValueError("All checkout parameters are required")
        
        if not isinstance(amount, (int, float)) or amount <= 0:
            raise ValueError("Amount must be a positive number")
        
        self.accountNumber = str(accountNumber).strip()
        self.amount = float(amount)
        self.externalId = str(externalId).strip()
        self.provider = str(provider).strip()
        self.logger = logging.getLogger(__name__)
        
        # Validate and normalize provider
        from .azam_res_models import PaymentProvider
        if not PaymentProvider.is_valid_provider(self.provider):
            valid_providers = PaymentProvider.get_all_providers()
            raise ValueError(f"Invalid provider. Must be one of: {', '.join(valid_providers)}")
        
        self.provider = PaymentProvider.normalize_provider(self.provider)
        
        # Initialize authentication
        try:
            self.auth = Authentication(
                client_id=settings.AZAM_PAY_CLIENT_ID,
                client_secret=settings.AZAM_PAY_CLIENT_SECRET,
                app_name=settings.AZAM_PAY_APP_NAME,
            )
        except Exception as e:
            self.logger.error(f"Failed to initialize authentication: {str(e)}")
            raise Exception(f"Authentication initialization failed: {str(e)}")

    def initCheckout(self):
        """Initialize a payment checkout"""
        try:
            # Get fresh token
            token = self.auth.get_token()
            
            url = settings.AZAM_PAY_CHECKOUT_URL + "/azampay/mno/checkout"
            
            payload = {
                "accountNumber": self.accountNumber,
                "additionalProperties": {"property1": None, "property2": None},
                "amount": self.amount,
                "currency": "TZS",
                "externalId": self.externalId,
                "provider": self.provider,
            }
            
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {token}",
                "User-Agent": "Vista-Backend/1.0"
            }
            
            self.logger.info(f"Initiating checkout for external ID: {self.externalId}")
            
            response = requests.post(
                url, 
                headers=headers, 
                data=json.dumps(payload)
                # No timeout for sandbox - allows longer response times
            )
            
            response.raise_for_status()
            response_data = response.json()
            
            self.logger.info(f"Checkout response received for external ID: {self.externalId}")
            return response_data
            
        except RequestException as e:
            self.logger.error(f"Network error during checkout: {str(e)}")
            raise Exception(f"Payment request failed: {str(e)}")
        except json.JSONDecodeError as e:
            self.logger.error(f"Invalid JSON response during checkout: {str(e)}")
            raise Exception("Invalid response from payment gateway")
        except Exception as e:
            self.logger.error(f"Checkout error: {str(e)}")
            raise Exception(f"Checkout failed: {str(e)}")
    


    def verify_payment(self, transaction_id):
        """Verify a payment transaction"""
        try:
            if not transaction_id:
                raise ValueError("Transaction ID is required")
            
            token = self.auth.get_token()
            url = settings.AZAM_PAY_CHECKOUT_URL + f"/azampay/mno/checkout/verify/{transaction_id}"
            
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {token}",
                "User-Agent": "Vista-Backend/1.0"
            }
            
            self.logger.info(f"Verifying payment for transaction ID: {transaction_id}")
            
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            response_data = response.json()
            self.logger.info(f"Payment verification completed for transaction ID: {transaction_id}")
            
            return response_data
            
        except RequestException as e:
            self.logger.error(f"Network error during payment verification: {str(e)}")
            raise Exception(f"Payment verification failed: {str(e)}")
        except Exception as e:
            self.logger.error(f"Payment verification error: {str(e)}")
            raise Exception(f"Payment verification failed: {str(e)}")
    
    def get_payment_status(self, transaction_id):
        """Get the status of a payment transaction"""
        try:
            if not transaction_id:
                raise ValueError("Transaction ID is required")
            
            token = self.auth.get_token()
            url = settings.AZAM_PAY_CHECKOUT_URL + f"/azampay/mno/checkout/status/{transaction_id}"
            
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {token}",
                "User-Agent": "Vista-Backend/1.0"
            }
            
            self.logger.info(f"Getting payment status for transaction ID: {transaction_id}")
            
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            response_data = response.json()
            self.logger.info(f"Payment status retrieved for transaction ID: {transaction_id}")
            
            return response_data
            
        except RequestException as e:
            self.logger.error(f"Network error during status check: {str(e)}")
            raise Exception(f"Status check failed: {str(e)}")
        except Exception as e:
            self.logger.error(f"Status check error: {str(e)}")
            raise Exception(f"Status check failed: {str(e)}")
    
    def cancel_payment(self, transaction_id, reason="User requested cancellation"):
        """Cancel a payment transaction"""
        try:
            if not transaction_id:
                raise ValueError("Transaction ID is required")
            
            token = self.auth.get_token()
            url = settings.AZAM_PAY_CHECKOUT_URL + f"/azampay/mno/checkout/cancel"
            
            payload = {
                "transactionId": transaction_id,
                "reason": reason
            }
            
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {token}",
                "User-Agent": "Vista-Backend/1.0"
            }
            
            self.logger.info(f"Cancelling payment for transaction ID: {transaction_id}")
            
            response = requests.post(
                url, 
                headers=headers, 
                data=json.dumps(payload)
            )
            response.raise_for_status()
            
            response_data = response.json()
            self.logger.info(f"Payment cancelled for transaction ID: {transaction_id}")
            
            return response_data
            
        except RequestException as e:
            self.logger.error(f"Network error during payment cancellation: {str(e)}")
            raise Exception(f"Payment cancellation failed: {str(e)}")
        except Exception as e:
            self.logger.error(f"Payment cancellation error: {str(e)}")
            raise Exception(f"Payment cancellation failed: {str(e)}")
    
    def refund_payment(self, transaction_id, amount=None, reason="Refund requested"):
        """Refund a payment transaction"""
        try:
            if not transaction_id:
                raise ValueError("Transaction ID is required")
            
            # If no amount specified, refund the full amount
            refund_amount = amount if amount is not None else self.amount
            
            if refund_amount <= 0 or refund_amount > self.amount:
                raise ValueError("Invalid refund amount")
            
            token = self.auth.get_token()
            url = settings.AZAM_PAY_CHECKOUT_URL + f"/azampay/mno/checkout/refund"
            
            payload = {
                "transactionId": transaction_id,
                "amount": refund_amount,
                "reason": reason
            }
            
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {token}",
                "User-Agent": "Vista-Backend/1.0"
            }
            
            self.logger.info(f"Processing refund for transaction ID: {transaction_id}, amount: {refund_amount}")
            
            response = requests.post(
                url, 
                headers=headers, 
                data=json.dumps(payload)
            )
            response.raise_for_status()
            
            response_data = response.json()
            self.logger.info(f"Refund processed for transaction ID: {transaction_id}")
            
            return response_data
            
        except RequestException as e:
            self.logger.error(f"Network error during refund: {str(e)}")
            raise Exception(f"Refund failed: {str(e)}")
        except Exception as e:
            self.logger.error(f"Refund error: {str(e)}")
            raise Exception(f"Refund failed: {str(e)}")
    
    def validate_phone_number(self, phone_number, provider):
        """Validate phone number format for specific provider"""
        phone_patterns = {
            'Airtel': [r'^(078|068|075)\d{7}$'],
            'Tigo': [r'^(071|065|067)\d{7}$'],
            'Halopesa': [r'^(062|076)\d{7}$'],
            'Azampesa': [r'^(071|065|067|078|068|075|062|076)\d{7}$'],
            'Mpesa': [r'^(074|076)\d{7}$']
        }
        
        import re
        patterns = phone_patterns.get(provider, [])
        
        for pattern in patterns:
            if re.match(pattern, phone_number):
                return True
        
        return False
