import random
from django.contrib.auth import authenticate
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from rest_framework import  viewsets

from authentication.models import VerificationCode
from authentication.serializers import ResetPasswordConfirmSerializer, UserSerializer, VGuestRegisterSerializer
from django.utils import timezone
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.contrib.auth.models import Group
from datetime import timedelta
from django.contrib.auth.tokens import default_token_generator
from django.core.exceptions import ValidationError
from django.core.mail import BadHeaderError
from django.conf import settings
# from twilio.rest import Client
import logging as loggger



User = get_user_model()

class VCheckEmailExistence(APIView):
    
    def post(self, request):
        email = request.data.get('email')
        user = User.objects.filter(email=email)
        serializer = UserSerializer(user.first())
        if user.exists():
            return Response({
                'message': 'Login',
                'data': serializer.data,
                
                }, status=status.HTTP_400_BAD_REQUEST)
        return Response({
            'message': 'Email is available', 
            'data': serializer.data     
            }, status=status.HTTP_200_OK)
    

class VLoginView(APIView):
    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        password = request.data.get('password')
        user = authenticate(request, email=email, password=password)
        if user is not None:
            
            user.last_login = timezone.localtime(timezone.now())
            user.save()
        if user is not None:
            refresh = RefreshToken.for_user(user)
            return Response({
                "refresh": str(refresh),
                "access": str(refresh.access_token),
                 
            }, status=status.HTTP_200_OK)
        return Response({'error': 'Invalid Credentials'}, status=status.HTTP_401_UNAUTHORIZED)



class VRegisterView(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = VGuestRegisterSerializer

    def mask_email(self, email):
        name, domain = email.split('@')
        name = name[:1] + "***" + name[-1:] if len(name) > 1 else name + "***"
        return f"{name}@{domain}"

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user= serializer.save()
            otp = random.randint(100000, 999999)

            VerificationCode.objects.create( 
                user=user, 
                code=otp,
                created_at=timezone.localtime(timezone.now()))
            

            # add to Rental host's Group
            user_group, created = Group.objects.get_or_create(name='guest')
            if not user.groups.filter(name='guest').exists():
                user.groups.add(user_group)
            # Send email with OTP

            mail_subject = 'Activate your account.'
            message = render_to_string('activate_account.html', {
                'user': user,
                'otp': otp,
            })

            try:
                email = request.data['email']
                email = EmailMessage(mail_subject, message, to=[email])
                email.content_subtype = 'html'

                res = email.send()
            except:
                user.delete()  # Delete the user if sending the email fails
                loggger.error("Failed to send email.")

                return Response({"message": "Failed to send email."}, status=status.HTTP_400_BAD_REQUEST)

            masked_email = self.mask_email( request.data.get('email'))
            message = f"User created successfully. A verification code has been sent to your email ({masked_email}). Please verify your account immediately before the session expires in 5 minutes."
            return Response(
                {
                "message": message,
                "data": serializer.data

                }
            , status=status.HTTP_201_CREATED)
        else:   
            loggger.warning(serializer.errors, exc_info=True, extra={

                'request': request
            })
            
            return Response(
                {
                "message": serializer.errors
                }
                
                , status=status.HTTP_400_BAD_REQUEST)


class VResendOtpView(APIView):
    def post(self, request):
        otp = random.randint(100000, 999999)

        try:
            user = User.objects.get(email=request.data.get('email'))
        except User.DoesNotExist:
            return Response({'message': 'User does not exist'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            verification_model = VerificationCode.objects.get(user=user)
        except VerificationCode.DoesNotExist:
            return Response({'message': 'No verification code found for the given user'}, status=status.HTTP_400_BAD_REQUEST)
       
        time_remaining = verification_model.created_at + timedelta(minutes=5) - timezone.localtime(timezone.now())
        if time_remaining > timedelta(minutes=0):

            # If the time remaining is more than 0, return an error with the time remaining
            return Response({'message': f'Please wait for {time_remaining.seconds // 60} minutes and {time_remaining.seconds % 60} seconds before sending another OTP'}, status=status.HTTP_400_BAD_REQUEST)
    
        verification_model.code = otp
        verification_model.created_at = timezone.localtime(timezone.now())
        verification_model.save()
        mail_subject = 'Activate your account.'
        message = render_to_string('activate_account.html', {
            'user': user,
            'otp': otp,
        })
        try:
            email = EmailMessage(mail_subject, message, to=[request.data.get('email')])
            email.content_subtype = 'html'
            email.send()
            return Response({'message': 'OTP sent successfully'}, status=status.HTTP_200_OK)
        except:
            return Response({'message': 'Failed to send OTP'}, status=status.HTTP_400_BAD_REQUEST)
    

class VActivateAccountView(APIView):
    def post(self, request):
 
        try:
            user = User.objects.get(email=request.data.get('email'))
        except User.DoesNotExist:
            loggger.error('User does not exist.')
            return Response({'message': 'User does not exist'}, status=status.HTTP_400_BAD_REQUEST)
        otp =  request.data.get("otp", None)
        # user = User.objects.get(email=request.data.get('email'))
        verification_model = VerificationCode.objects.get(user=user)
        if verification_model.code == otp and timezone.localtime(timezone.now()) < verification_model.created_at + timedelta(minutes=5):
            user.is_active = True
            verification_model.otp_used = True
            verification_model.save() 
            user.save()
            return Response({'message': 'Account activated successfully'}, status=status.HTTP_200_OK)
        else:
            loggger.error('Invalid or expired OTP')
            return Response({'message': 'Invalid or expired OTP'}, status=status.HTTP_400_BAD_REQUEST)
        
class ResetPasswordInitView(APIView):
    def post(self, request):
        try:
            user = User.objects.get(email=request.data.get('email'))
            token = default_token_generator.make_token(user)
            mail_subject = 'Reset your password.'
            message = render_to_string('reset_password.html', {
                'user': user,
                'token': token,
            })
        except User.DoesNotExist:
            return Response({'error': 'User does not exist'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': 'An error occurred: {}'.format(str(e))}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        try:
            email = EmailMessage(mail_subject, message, to=[request.data.get('email')])
            email.content_subtype = 'html'

            email.send()
        except BadHeaderError:
            return Response({'error': 'Invalid header found.'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': 'An error occurred while sending the email: {}'.format(str(e))}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({'message': "Password reset OTP code has been sent to your email address. Please visit your email and use that code to confirm your password reset request."}, status=status.HTTP_200_OK)
    


class ResetPasswordConfirmView(APIView):

    def post(self, request):
        serializer = ResetPasswordConfirmSerializer(data=request.data)
        if serializer.is_valid():
           
            token = serializer.data.get('token')
            new_password = serializer.data.get('new_password')
            confirm_password = serializer.data.get('confirm_password')

            # Get the user
            try:
                user = User.objects.get(email=serializer.data.get('email'))
            except User.DoesNotExist:
                return Response({'message': 'User does not exist'}, status=status.HTTP_400_BAD_REQUEST)

            # Check if the new password and confirm password match
            if new_password != confirm_password:
                return Response({'message': 'Passwords do not match.'}, status=status.HTTP_400_BAD_REQUEST)

            # Check token
            if not default_token_generator.check_token(user, token):
                return Response({'message': 'Invalid token.'}, status=status.HTTP_400_BAD_REQUEST)

            # Set new password
            user.set_password(new_password)
            user.save()

            return Response({'message': 'Password reset successfully'}, status=status.HTTP_200_OK)
        else:

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        

class PhoneNumberAuthenticationView(APIView):
    def post(self, request):
        phone_number = request.data.get('phone_number')
        try:
            user = User.objects.get(phone_number=phone_number, is_active=True)
        except User.DoesNotExist:
            return Response({'message': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        if user:
            # Generate OTP
            otp = random.randint(100000, 999999)
            VerificationCode.objects.create(
                user=user,
                code=otp,
                created_at=timezone.localtime(timezone.now())
            )

            # Send OTP via SMS (assuming the method is defined in the same class or elsewhere)
            self.send_otp_sms(phone_number, otp)

            return Response({
                "alternative_otps": otp,
                'message': 'OTP sent successfully. Please use it to login.'
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'message': 'No active user found with the provided phone number.'
            }, status=status.HTTP_404_NOT_FOUND)

    def send_otp_sms(self, phone_number, otp):
        # Implementation for sending OTP via SMS
        pass




class VerifyPhoneAndLoginView(APIView):
    """
    Verify phone number and login
    """
    def post(self, request):
        phone_number = request.data.get('phone_number')
        otp = request.data.get('otp')

        if not phone_number or not otp:
            return Response({'message': 'Phone number and OTP are required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(phone_number=phone_number, is_active=True)
        except User.DoesNotExist:
            return Response({'message': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        try:
            verification_code = VerificationCode.objects.get(user=user, code=otp)
        except VerificationCode.DoesNotExist:
            return Response({'message': 'Invalid OTP'}, status=status.HTTP_400_BAD_REQUEST)

        # Check if OTP has expired
        if timezone.localtime(timezone.now()) > verification_code.created_at + timedelta(minutes=5):
            return Response({'message': 'OTP has expired'}, status=status.HTTP_400_BAD_REQUEST)

        # If user's phone is not verified, verify it
        if not user.phone_is_verified:
            user.phone_is_verified = True
            user.save()

        # Generate tokens
        refresh = RefreshToken.for_user(user)
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }, status=status.HTTP_200_OK)
        

