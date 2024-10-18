import requests

def get_state_data(id):
        url = f"http://192.168.7.49:8123/api/states/{id}"  # Example: light.qhm_1cc9
        headers = {
            "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiI3ZjUyNzdmZTliM2M0ODY2YjkyNTA5ODViMzk4OWRiZSIsImlhdCI6MTcyOTA0NTY0MCwiZXhwIjoyMDQ0NDA1NjQwfQ.-67y0JjE6-2PP4daJnsO4AafUxAG9rfNv8kC6Ieu9Yc",
            "content-type": "application/json"
        }
        response = requests.get(url, headers=headers)
        return response.json()

def post_state(service, method, id):
        """Post state changes to the entity."""
        headers = {
            "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiI3ZjUyNzdmZTliM2M0ODY2YjkyNTA5ODViMzk4OWRiZSIsImlhdCI6MTcyOTA0NTY0MCwiZXhwIjoyMDQ0NDA1NjQwfQ.-67y0JjE6-2PP4daJnsO4AafUxAG9rfNv8kC6Ieu9Yc"
        }
        data = {"entity_id": id}
        requests.post(f"http://192.168.7.49:8123/api/services/{service}/{method}", headers=headers, json=data)
        return
    