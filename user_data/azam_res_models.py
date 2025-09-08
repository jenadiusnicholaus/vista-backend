from dataclasses import dataclass
from typing import Optional, Dict, Any
import json


@dataclass
class AccessToken:
    """Access token data structure"""
    type: str
    value: Optional[str] = None
    expires_at: Optional[str] = None


@dataclass
class AuthData:
    """Authentication response data structure"""
    accessToken: str
    refreshToken: Optional[str] = None
    tokenType: str = "Bearer"
    expire: Optional[str] = None


@dataclass
class AuthResponse:
    """Authentication API response structure"""
    data: AuthData
    message: str
    success: bool
    statusCode: int


class TransactionResponse:
    """Payment transaction response handler"""
    
    def __init__(self, success=False, transactionId=None, message=None, messageCode=None, **kwargs):
        self.success = success
        self.transactionId = transactionId
        self.message = message
        self.messageCode = messageCode
        
        # Store additional fields
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        """Create TransactionResponse from dictionary"""
        if not isinstance(data, dict):
            raise ValueError("Data must be a dictionary")
        
        return cls(
            success=data.get('success', False),
            transactionId=data.get('transactionId'),
            message=data.get('message'),
            messageCode=data.get('messageCode'),
            **{k: v for k, v in data.items() if k not in ['success', 'transactionId', 'message', 'messageCode']}
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'success': self.success,
            'transactionId': self.transactionId,
            'message': self.message,
            'messageCode': self.messageCode
        }
    
    def __str__(self):
        return f"TransactionResponse(success={self.success}, transactionId={self.transactionId}, message='{self.message}')"


class PaymentStatus:
    """Payment status constants"""
    PENDING = 'PENDING'
    SUCCESS = 'SUCCESS'
    FAILED = 'FAILED'
    CANCELLED = 'CANCELLED'
    REFUNDED = 'REFUNDED'
    
    @classmethod
    def is_valid_status(cls, status: str) -> bool:
        """Check if status is valid"""
        return status.upper() in [cls.PENDING, cls.SUCCESS, cls.FAILED, cls.CANCELLED, cls.REFUNDED]


class PaymentProvider:
    """Payment provider constants - matching Azam Pay API specification"""
    AIRTEL = 'Airtel'
    TIGO = 'Tigo'
    HALOPESA = 'Halopesa'
    AZAMPESA = 'Azampesa'
    MPESA = 'Mpesa'
    
    @classmethod
    def get_all_providers(cls) -> list:
        """Get all available providers"""
        return [cls.AIRTEL, cls.TIGO, cls.HALOPESA, cls.AZAMPESA, cls.MPESA]
    
    @classmethod
    def is_valid_provider(cls, provider: str) -> bool:
        """Check if provider is valid"""
        return provider.capitalize() in cls.get_all_providers()
    
    @classmethod
    def normalize_provider(cls, provider: str) -> str:
        """Normalize provider name to correct capitalization"""
        return provider.capitalize() if provider else provider


@dataclass
class WebhookData:
    """Webhook notification data structure"""
    transactionId: str
    externalId: str
    status: str
    message: str
    amount: Optional[float] = None
    currency: str = 'TZS'
    timestamp: Optional[str] = None
    
    def __post_init__(self):
        """Validate webhook data after initialization"""
        if not PaymentStatus.is_valid_status(self.status):
            raise ValueError(f"Invalid payment status: {self.status}")
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        """Create WebhookData from dictionary"""
        return cls(
            transactionId=data.get('transactionId'),
            externalId=data.get('externalId'),
            status=data.get('status'),
            message=data.get('message'),
            amount=data.get('amount'),
            currency=data.get('currency', 'TZS'),
            timestamp=data.get('timestamp')
        )
