# Azam Pay Integration Documentation

## Overview

This document provides comprehensive information about the improved Azam Pay integration for the Vista property management system. The integration supports mobile money payments for property bookings and rentals in Tanzania.

## Features

### ✅ Implemented Features

- **Secure Authentication**: Token-based authentication with automatic refresh
- **Payment Processing**: Support for all major Tanzanian mobile networks
- **Webhook Handling**: Real-time payment status updates
- **Input Validation**: Comprehensive validation for phone numbers, amounts, and providers
- **Error Handling**: Robust error handling with proper logging
- **Payment Status Tracking**: Complete payment lifecycle management
- **Phone Number Validation**: Network-specific phone number validation
- **Transaction Management**: Full CRUD operations for payments

### 🔧 Supported Mobile Networks

- **Airtel**: 078, 068, 075
- **Tigo**: 071, 065, 067
- **Halopesa**: 062, 076
- **Azampesa**: All supported networks
- **M-Pesa**: 074, 076

## File Structure

```
user_data/
├── azam_pay_auth.py          # Authentication management
├── azam_pay_checkout.py      # Payment processing
├── azam_pay_urls.py          # API endpoint URLs
├── azam_pay_webhooks.py      # Webhook handlers
├── azam_res_models.py        # Response models and constants
├── payment_utils.py          # Utility functions
├── booking_views.py          # Booking payment views (improved)
├── renting_views.py          # Renting payment views (improved)
└── models.py                 # Database models (fixed)
```

## Configuration

### Environment Variables

Add these to your `.env` file:

```env
# Azam Pay Configuration
AZAM_PAY_AUTH=https://authenticator-sandbox.azampay.co.tz
AZAM_PAY_CHECKOUT_URL=https://sandbox.azampay.co.tz
AZAM_PAY_APP_NAME=your_app_name
AZAM_PAY_CLIENT_ID=your_client_id
AZAM_PAY_CLIENT_SECRET=your_client_secret
```

### Django Settings

The following settings are already configured in `settings.py`:

```python
# AZAM PAY
AZAM_PAY_AUTH = config("AZAM_PAY_AUTH", default="no_auth")
AZAM_PAY_CHECKOUT_URL = config("AZAM_PAY_CHECKOUT_URL", default="no_checkout_url")
AZAM_PAY_APP_NAME = config("AZAM_PAY_APP_NAME", default="no_app_name")
AZAM_PAY_CLIENT_ID = config("AZAM_PAY_CLIENT_ID", default="no_client_id")
AZAM_PAY_CLIENT_SECRET = config("AZAM_PAY_CLIENT_SECRET", default="no_client_secret")
```

## API Endpoints

### Booking Payments

#### Create Booking Payment
```http
POST /api/v1/user-data/confirm-booking/?booking_id={booking_id}
```

**Request Body:**
```json
{
    "payment_method": "AIRTEL",
    "accountNumber": "0781234567",
    "amount": 50000
}
```

**Response (Success):**
```json
{
    "message": "Booking confirmed successfully."
}
```

### Renting Payments

#### Create Renting Payment
```http
POST /api/v1/user-data/confirm-renting-mwm/?renting_id={renting_id}
```

**Request Body:**
```json
{
    "payment_method": "TIGO",
    "accountNumber": "0711234567",
    "amount": 100000
}
```

### Webhook Endpoints

#### Azam Pay Webhook
```http
POST /api/v1/user-data/azam-pay/webhook/
```

**Webhook Payload:**
```json
{
    "transactionId": "TXN123456789",
    "externalId": "booking_or_renting_id",
    "status": "SUCCESS",
    "message": "Payment completed successfully",
    "amount": 50000,
    "currency": "TZS"
}
```

#### Payment Status Check
```http
POST /api/v1/user-data/azam-pay/status-check/
```

**Request Body:**
```json
{
    "transaction_id": "TXN123456789"
}
```

## Usage Examples

### Basic Payment Processing

```python
from user_data.payment_utils import PaymentProcessor

# Initialize processor for booking
processor = PaymentProcessor(user=request.user, booking_id="123")

# Process payment
payment_data = {
    "payment_method": "AIRTEL",
    "accountNumber": "0781234567",
    "amount": 50000
}

result = processor.process_payment(payment_data)

if result['success']:
    print(f"Payment initiated: {result['transaction_id']}")
else:
    print(f"Payment failed: {result['message']}")
```

### Phone Number Validation

```python
from user_data.payment_utils import PaymentValidator

# Validate phone number
is_valid, error = PaymentValidator.validate_phone_number("0781234567", "AIRTEL")

if is_valid:
    print("Phone number is valid")
else:
    print(f"Validation error: {error}")
```

### Payment Status Management

```python
from user_data.payment_utils import PaymentStatusManager

# Get payment status
status = PaymentStatusManager.get_payment_status("TXN123456789")

if status:
    print(f"Payment type: {status['type']}")
    print(f"Status: {'Completed' if status['completed'] else 'Pending'}")
```

## Error Handling

### Common Error Responses

#### Invalid Phone Number
```json
{
    "message": "Invalid phone number format. Must be a valid Tanzanian mobile number"
}
```

#### Invalid Provider
```json
{
    "message": "Invalid payment method. Must be one of: AIRTEL, TIGO, HALOPESA, AZAMPESA, MPESA"
}
```

#### Network Mismatch
```json
{
    "message": "Phone number 0781234567 is not valid for TIGO network"
}
```

#### Missing Parameters
```json
{
    "message": "Missing required parameters: payment_method, accountNumber, amount"
}
```

### Error Logging

All errors are logged with appropriate log levels:

```python
import logging
logger = logging.getLogger(__name__)

# Error logging examples
logger.error(f"Payment processing failed: {str(e)}")
logger.warning(f"Invalid payment attempt from user {user.id}")
logger.info(f"Payment initiated successfully: {transaction_id}")
```

## Security Features

### Input Validation
- Phone number format validation
- Amount range validation (100 - 10,000,000 TZS)
- Provider validation
- User authorization checks

### Authentication
- Secure token management
- Automatic token refresh
- Request timeout handling
- Error response sanitization

### Data Protection
- Sensitive data logging prevention
- Secure webhook validation
- User data access control

## Testing

### Manual Testing Checklist

#### Booking Payment Flow
1. ✅ Create a booking
2. ✅ Initiate payment with valid data
3. ✅ Verify payment record creation
4. ✅ Test webhook reception
5. ✅ Verify status updates

#### Renting Payment Flow
1. ✅ Create a renting request
2. ✅ Initiate payment with valid data
3. ✅ Verify payment record creation
4. ✅ Test webhook reception
5. ✅ Verify status updates

#### Error Scenarios
1. ✅ Invalid phone number
2. ✅ Invalid provider
3. ✅ Network mismatch
4. ✅ Missing parameters
5. ✅ Unauthorized access
6. ✅ Invalid amount

### Test Phone Numbers

Use these test numbers for different networks:

```python
TEST_NUMBERS = {
    'AIRTEL': '0781234567',
    'TIGO': '0711234567',
    'HALOPESA': '0621234567',
    'MPESA': '0741234567'
}
```

## Monitoring and Logging

### Log Levels

- **INFO**: Successful operations, payment initiations
- **WARNING**: Invalid attempts, validation failures
- **ERROR**: System errors, API failures
- **DEBUG**: Detailed request/response data (development only)

### Key Metrics to Monitor

1. **Payment Success Rate**: Percentage of successful payments
2. **Response Times**: API response times
3. **Error Rates**: Failed payment attempts
4. **Network Distribution**: Usage by mobile network
5. **Webhook Delivery**: Webhook success rates

## Troubleshooting

### Common Issues

#### Authentication Failures
```python
# Check credentials in settings
AZAM_PAY_CLIENT_ID = "your_actual_client_id"
AZAM_PAY_CLIENT_SECRET = "your_actual_secret"
```

#### Webhook Not Received
1. Verify webhook URL is accessible
2. Check firewall settings
3. Validate webhook endpoint configuration
4. Review Azam Pay dashboard settings

#### Payment Status Not Updating
1. Check webhook processing logs
2. Verify database connections
3. Review serializer validations
4. Check for transaction ID mismatches

### Debug Mode

Enable debug logging for detailed information:

```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': 'azam_pay.log',
        },
    },
    'loggers': {
        'user_data.azam_pay_auth': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'user_data.azam_pay_checkout': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}
```

## Migration Guide

### Database Migrations

Run migrations to apply model fixes:

```bash
python manage.py makemigrations user_data
python manage.py migrate
```

### Updating Existing Code

If you have existing payment code, update it to use the new utilities:

```python
# Old way
azmpay = AzamPayCheckout(accountNumber, amount, externalId, provider)
response = azmpay.initCheckout()

# New way
from user_data.payment_utils import PaymentProcessor

processor = PaymentProcessor(user=request.user, booking_id=booking_id)
result = processor.process_payment(payment_data)
```

## Performance Optimization

### Caching
- Token caching with expiry
- Payment status caching
- Network validation caching

### Database Optimization
- Proper indexing on transaction_id fields
- Optimized queries for payment lookups
- Connection pooling for high traffic

## Support and Maintenance

### Regular Maintenance Tasks

1. **Token Cleanup**: Remove expired tokens
2. **Log Rotation**: Manage log file sizes
3. **Status Monitoring**: Check payment success rates
4. **Security Updates**: Keep dependencies updated

### Contact Information

For technical support or questions about this integration:

- **Developer**: Vista Backend Team
- **Documentation**: This README file
- **Issue Tracking**: Project repository issues

---

## Changelog

### Version 2.0.0 (Current)
- ✅ Complete rewrite of authentication system
- ✅ Added comprehensive input validation
- ✅ Implemented webhook handling
- ✅ Added payment utility functions
- ✅ Improved error handling and logging
- ✅ Fixed syntax errors in models
- ✅ Added phone number validation
- ✅ Enhanced security features

### Version 1.0.0 (Previous)
- Basic payment processing
- Simple authentication
- Limited error handling
- Debug prints in production code
- Incomplete webhook support
