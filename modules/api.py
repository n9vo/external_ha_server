import requests
import json

json_Data = json.load(open('../config.json', 'r'))

ip = json_Data['ha_ip']
token = json_Data['ha_token']

def get_state_data(id):
        url = f"http://{ip}:8123/api/states/{id}"  # Example: light.qhm_1cc9
        headers = {
            "Authorization": f"Bearer {token}",
            "content-type": "application/json"
        }
        response = requests.get(url, headers=headers)
        return response.json()

def post_state(service, method, id):
        """Post state changes to the entity."""
        headers = {
                "Authorization": f"Bearer {token}"
        }
        data = {"entity_id": id}
        requests.post(f"http://{ip}:8123/api/services/{service}/{method}", headers=headers, json=data)
        return
    
