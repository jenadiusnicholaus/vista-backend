import requests
from django.conf import settings 
import json   

class EjabberdApi:
    def __init__(self, access_token):
        self.access_token = access_token
        self.headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json',
        }       

    def setPresence(self, user, host, resource, type, show, status, priority):
        url = settings.EJABBERD_API_BU + "/api/set_presence"
        payload = json.dumps({
        "user": user,
        "host": host,  
        "resource": resource,
        "type": type,
        "show": show,
        "status": status,
        "priority": priority
        })
        headers = self.headers

        response = requests.request("POST", url, headers=headers, data=payload)
        return response

    def getPresence(self, user, host):
        url = settings.EJABBERD_API_BU + "/api/get_presence"
        payload = json.dumps({
        "user": user,
        "host": host
        })
        headers = self.headers

        response = requests.request("POST", url, headers=headers, data=payload)
        return response 
    
    def getRoster(self, user, host):
        url = settings.EJABBERD_API_BU + "/api/get_roster"
        payload = json.dumps({
        "user": user,
        "host": host
        })
        headers = self.headers

        response = requests.request("POST", url, headers=headers, data=payload)
        return response
    

    def addRosterItem(self, localuser, localserver, user, server, nick, groupNames, subs):
        url = settings.EJABBERD_API_BU + "/api/add_rosteritem"
        payload = json.dumps({
        "localuser": localuser,
        "localserver": localserver,
        "user": user,
        "server": server,
        "nick": nick,
        "groups": [],
        'subs': 'both'
        })

        print(payload)
        headers = self.headers

        response = requests.request("POST", url, headers=headers, data=payload)
        return response
    

    def sendMailMessage(self, from_user, to_user, message):
      
        url = settings.EJABBERD_API_BU + "/api/send_message"
        payload = json.dumps({
        "type": "chat",
        "from": from_user,
        "to": to_user,
        "subject": "Message",
        "body": message
        })  
        headers = self.headers  
        response = requests.request("POST", url, headers=headers, data=payload)
        return response
    
    #POST /api/send_stanza
    # {
    #   "from": "admin@localhost",
    #   "to": "user1@localhost",
    #   "stanza": "<message><ext attr='value'/></message>"
    # }

    def sendStanza(self, from_user, to_user, stanza):
        url = settings.EJABBERD_API_BU + "/api/send_stanza"
        payload = json.dumps({
        "from": from_user,
        "to": to_user,
        "stanza": stanza
        })  
        headers = self.headers  
        response = requests.request("POST", url, headers=headers, data=payload)
        return response

        
        


        
