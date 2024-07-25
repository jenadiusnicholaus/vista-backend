from django.conf import settings
import requests
import json

from authentication.models import AzamPayAuthToken

from .azam_pay_urls import AzamPayUrls
from .azam_pay_auth import Authentication


class AzamPayCheckout:
    def __init__(self, accountNumber, amount, externalId, provider):
        self.accountNumber = accountNumber
        self.amount = amount

        self.externalId = externalId
        self.provider = provider
        self.token = Authentication(
            client_id=settings.AZAM_PAY_CLIENT_ID,
            client_secret=settings.AZAM_PAY_CLIENT_SECRET,
            app_name=settings.AZAM_PAY_APP_NAME,
        ).get_token()

    def initCheckout(self):
        url = settings.AZAM_PAY_CHECKOUT_URL + "/azampay/mno/checkout"
        payload = json.dumps(
            {
                "accountNumber": self.accountNumber,
                "additionalProperties": {"property1": None, "property2": None},
                "amount": self.amount,
                "currency": "TZS",
                "externalId": self.externalId,
                "provider": self.provider,
            }
        )

 


        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer  {self.token}",
        }

        print(headers)


        response = requests.request("POST", url, headers=headers, data=payload)
        print(response.text)
        return response.text
    


    def verify(self, data):
        # Verify a checkout
        pass

    def cancel(self, data):
        # Cancel a checkout
        pass

    def refund(self, data):
        # Refund a checkout
        pass

    def status(self, data):
        # Get the status of a checkout
        pass
