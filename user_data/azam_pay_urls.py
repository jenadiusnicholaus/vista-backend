from django.conf import settings


class AzamPayUrls:

    def getTokeUrl(self):
        # https://authenticator-sandbox.azampay.co.tz/AppRegistration/GenerateToken
        return settings.AZAM_PAY_AUTH + "/AppRegistration/GenerateToken"

    def getCheckoutUrl(self):
        #    https://sandbox.azampay.co.tz/azampay/mno/checkout
        return settings.AZAM_PAY_CHECKOUT_URL
