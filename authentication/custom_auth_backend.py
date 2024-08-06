# from django.contrib.auth.backends import BaseBackend
# from django.contrib.auth import get_user_model
# from django.core.exceptions import MultipleObjectsReturned
# User = get_user_model()

# class PhoneAuthBackend(BaseBackend):
#     def authenticate(self, request, username=None, phone=None, password=None, **kwargs):
#         try:
#             if phone is None:
               
#                 user = User.objects.get(phone_number=phone)
#             else:
#                 user = User.objects.get(email=username)

#             if user.check_password(password):
#                 print("User authenticated")
#                 return user
            
#         except User.DoesNotExist:
#             print("User does not exist")
#             return None
#         except MultipleObjectsReturned:
#             # Handle the case where multiple users have the same phone number
#             return None

#     def get_user(self, user_id):
#         try:
#             return User.objects.get(pk=user_id)
#         except User.DoesNotExist:
#             return None
