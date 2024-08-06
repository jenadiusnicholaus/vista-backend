#!/usr/bin/env python
import os
import sys
import struct
import logging
import django


# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vasta_settings.settings')
django.setup()

from django.contrib.auth import authenticate, get_user_model
from django.conf import settings

# Set up logging
log_file_path = os.path.join(settings.BASE_DIR, 'ejabberd_auth_bridge.log')
sys.stderr = open(log_file_path, 'w')
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(message)s',
                    filename=log_file_path,
                    filemode='a')

User = get_user_model()


def from_ejabberd():
    input_length = sys.stdin.buffer.read(2)
    (size,) = struct.unpack('>h', input_length)
    return sys.stdin.read(size).split(':')

def to_ejabberd(bool):
    answer = 0
    if bool:
        answer = 1
    token = struct.pack('>hh', 2, answer)
    sys.stdout.buffer.write(token)
    sys.stdout.flush()
def get_user_by_phone(phone):
    try:
        user = User.objects.get(phone_number=phone)
        return user
    except User.DoesNotExist:
        return None 

def auth(username, server, password):
    logging.info('Starting authentication for user: %s', username)
    user = get_user_by_phone(username)
    authenticated_user = authenticate(username=user.email, password=password)
    if authenticated_user is not None:
        logging.info('User authenticated: %s', username)
        return True
    else:
        logging.error('User not authenticated: %s', username)
        logging.error(user.email)
        return False



def isuser(username, server):
    User = get_user_model()
    logging.info(f"Checking if user {username} exists")
    user = get_user_by_phone(username)

    return User.objects.filter(phone_number=username).exists()

def setpass(username, server, password):
    try:
        user = User.objects.get(phone_number=username)
        user.set_password(password)
        user.save()
        return True
    except User.DoesNotExist:
        return False
    
def check_password(username, password):
    logging.info(f"Password check for {username}")

    try:
        _user = get_user_by_phone(username)
        user = authenticate(username=_user.email, password=password)
        result = user is not None
        logging.info(f"Password check for {username}: {result}")
        return result
    except Exception as e:
        logging.error(f"Error checking password for {username}: {e}")
        return False

while True:
    data = from_ejabberd()
    logging.info('Received data: %s', data)
    success = False
    if data[0] == "auth":
        success = auth(data[1], data[2], data[3])
        logging.info('Auth success: %s', success)
    elif data[0] == "isuser":
        success = isuser(data[1], data[2])
        logging.info('Isuser success: %s', success)
    elif data[0] == "setpass":
        success = setpass(data[1], data[2], data[3])
        logging.info('Setpass success: %s', success)
    elif data[0] == "check_password":
        success = check_password(data[1], data[2])
        logging.info('Check password success: %s', success)
    logging.info('Sending success: %s', success)
    to_ejabberd(success)