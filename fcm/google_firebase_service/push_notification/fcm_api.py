# FCM endpoint
import json
import requests


class FCM:
    def __init__(self, project_id, access_token):
        self.project_id = project_id
        self.access_token = access_token
        self.url = f'https://fcm.googleapis.com/v1/projects/{project_id}/messages:send'
        self.headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json; UTF-8',
        }

    def send_notification(self, device_registration_token, title, body, data):
        payload = {
            "message": {
                "token": device_registration_token,
                "notification": {
                    "title": title,
                    "body": body
                },
                "data": data
            }
        }
        response = requests.post(self.url, headers=self.headers, data=json.dumps(payload))
        return response.status_code, response.json()    
