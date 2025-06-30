from time import time


import jwt
import requests
import json


class Zoom():
    def __init__(self, key, secret):
        self.key = key
        self.secret = secret

    def get_token(self):
        return jwt.encode(
                {'iss': self.key, 'exp': time() + 5000},
                self.secret,
                algorithm='HS256'
            )

    def create_meeting_obj(self, topic, meeting_type, time):
        return {
            'topic': topic,
            'type': meeting_type,
            'start_time': time,
            'duration': '45',
            'timezone': 'Asia/Kolkata',
            'settings': {
                'host_video': False,
                'participant_video': True,
                'in_meeting': True,
                'join_before_host': False,
                'waiting_room': True,
                'mute_upon_entry': True,
                'audio': 'voip',
                'allow_multiple_devices': True
            },
            'pre_schedule': False
        }

    def schedule_meeting(self, data):
        headers = {
            'authorization': 'Bearer %s' % self.get_token(),
            'content-type': 'application/json'
        }

        response = requests.post(
            f'https://api.zoom.us/v2/users/me/meetings', 
            headers=headers, data=json.dumps(data))

        meeting = json.loads(response.text)

        return data['start_time'], meeting['join_url'], str(meeting['id']), meeting['password']
