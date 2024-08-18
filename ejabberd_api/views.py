from django.shortcuts import render

# Create your views here.
# from pyejabberd import EjabberdAPIClient # type: ignore

from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import json 
from xml.sax.saxutils import escape
import logging 
from django.contrib.auth import get_user_model
from authentication.serializers import UserSerializer 
from rest_framework import viewsets
User = get_user_model()





from .ejabberd_api import EjabberdApi


api = EjabberdApi(settings.EJABBERD_API_ACCESS_TOKEN)


class EjabberdSetPresenceView(APIView):
    def post(self, request):
        # Get the key from the QueryDict
        json_string = list(request.data.keys())[0]

        # Convert the JSON string to a dictionary
        data = json.loads(json_string)

        # Now you can access the values in the dictionary
        user = data.get("user")
        host = data.get("host")
        resource = data.get("resource")
        type = data.get("type")
        show = data.get("show")
        _status = data.get("status")
        priority = data.get("priority")
        priority = int(priority)


        try:

            response = api.setPresence(user, host, resource, type, show, _status, priority)
            if response.status_code == 200  :
                return Response(response.json(), status=status.HTTP_200_OK)
        
            return Response(response.json(), status=status.HTTP_400_BAD_REQUEST)
        except ValueError as e: 
            print(e) 

            return Response({"error": f"{e}"}, status=status.HTTP_400_BAD_REQUEST)
       
       
    
    
class EjabberdgetPresenceView(APIView):
    def post(self, request):
        # Get the key from the QueryDict
        json_string = list(request.data.keys())[0]

        # Convert the JSON string to a dictionary
        data = json.loads(json_string)

        # Now you can access the values in the dictionary
        user = data.get("user")
        host = data.get("host")

        response = api.getPresence(user, host)

        if response.status_code == 200:
            return Response(response.json(), status=status.HTTP_200_OK)
        
        return Response(response.json(), status=status.HTTP_400_BAD_REQUEST)
    
class EjabberdgetRosterView(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    # same as post
    def create(self, request):
        username = request.data.get("user")
        host = request.data.get("host")
        
        try:
            response = api.getRoster(username, host)
        except Exception as e:
            return Response({"message": "Can't get Contacts", "error": str(e)}, status=status.HTTP_404_NOT_FOUND)

        rosters = []
        if response.status_code == 200:
            for roster in response.json():
                phone_number = roster['jid'].split('@')[0]
                try:
                    user = User.objects.get(phone_number=phone_number)
                    user_serializer = self.get_serializer(user)
                    rosters.append(user_serializer.data)
                except User.DoesNotExist:
                    pass  # Skip users that do not exist in the database

            return Response(rosters, status=status.HTTP_200_OK)
        
        return Response(response.json(), status=status.HTTP_400_BAD_REQUEST)

       
    
class EjabberdAddRosterItemView(APIView):
    def post(self, request):
        print(request.data)
        data = request.data
        # Now you can access the values in the dictionary
        localuser = data.get("localuser")
        localserver = data.get("localhost")
        user = data.get("user")
        server = data.get("host")
        nick = data.get("nick")
        group = []
        subs= ''

        response = api.addRosterItem(localuser, localserver, user, server, nick, group, subs    )

        if response.status_code == 200:
            return Response(response.json(), status=status.HTTP_200_OK)
        
        return Response(response.json(), status=status.HTTP_400_BAD_REQUEST)
    
class EjabberdSendStanzaMessage(APIView):
    def post(self, request):
       # Assuming request.data.get() returns None if the key doesn't exist
        from_user = request.data.get("from")
        to_user = request.data.get("to")
        message = request.data.get("message")
        from_user_escaped = escape(from_user) if from_user else ""
        to_user_escaped = escape(to_user) if to_user else ""
        message_escaped = escape(message) if message else ""

        stanza = f"<message from='{from_user_escaped}' to='{to_user_escaped}' type='chat'><body>{message_escaped}</body></message>"
        response = api.sendStanza(from_user, to_user, stanza)

        if response.status_code == 200:
            return Response(response.json(), status=status.HTTP_200_OK)
        return Response(response.json(), status=status.HTTP_400_BAD_REQUEST)
    

class EjabberdRetrieveMessages(APIView):
    def post(self, request):
        from_user = request.data.get("from")
        to_user = request.data.get("to")
        from_user_escaped = escape(from_user) if from_user else ""
        to_user_escaped = escape(to_user) if to_user else ""

        # Ensure the MAM query stanza is correctly formatted
        mam_query_stanza = """
        <iq type='set' id='mamQuery1'>
        <query xmlns='urn:xmpp:mam:2'>
            <x xmlns='jabber:x:data' type='submit'>
            <field var='FORM_TYPE' type='hidden'>
                <value>urn:xmpp:mam:2</value>
            </field>
            <!-- Optionally, specify a date range or other parameters here -->
            </x>
        </query>
        </iq>
        """

        try:
            response = api.sendStanza(from_user_escaped, to_user_escaped, mam_query_stanza)
            if response.status_code == 200:
                # Parse the response to extract messages
                messages = self.parse_messages(response.json())
                return Response({"messages": messages}, status=status.HTTP_200_OK)
            else:
                logging.error(f"Failed to retrieve messages: {response.text}")
                return Response({"error": "Failed to retrieve messages"}, status=response.status_code)
        except Exception as e:
            logging.exception("An error occurred while retrieving messages.")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def parse_messages(self, response_data):
        # Implement parsing logic based on the actual structure of response_data
        # This is a placeholder function and needs to be implemented
        return response_data  # Placeholder return

      
       

        
      

       


