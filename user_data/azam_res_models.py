from dataclasses import dataclass


@dataclass
class AccessToken:
    type: str


@dataclass
class Data:
    accessToken: AccessToken
    expire: AccessToken


@dataclass
class Response:
    data: Data
    message: str
    success: bool
    statusCode: int


class TransactionResponse:
    def __init__(self, success, transactionId, message, messageCode):
        self.success = success
        self.transactionId = transactionId
        self.message = message
        self.messageCode = messageCode
