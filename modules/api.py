import requests

def get_state_data(id):
        url = f"http://192.168.7.49:8123/api/states/{id}"  # Example: light.qhm_1cc9
        headers = {
            "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJiODcwOTE3MTRmMDQ0YjZmOTI4MWM5OGY4OTc2OTQ4NSIsImlhdCI6MTcyOTM4MzQzNCwiZXhwIjoyMDQ0NzQzNDM0fQ.HqjF4wXkT9TmZkvJJT-kYep4cY8LASnvYjibGZmFp1Q",
            "content-type": "application/json"
        }
        response = requests.get(url, headers=headers)
        return response.json()

def post_state(service, method, id):
        """Post state changes to the entity."""
        headers = {
            "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJiODcwOTE3MTRmMDQ0YjZmOTI4MWM5OGY4OTc2OTQ4NSIsImlhdCI6MTcyOTM4MzQzNCwiZXhwIjoyMDQ0NzQzNDM0fQ.HqjF4wXkT9TmZkvJJT-kYep4cY8LASnvYjibGZmFp1Q"
        }
        data = {"entity_id": id}
        requests.post(f"http://192.168.7.49:8123/api/services/{service}/{method}", headers=headers, json=data)
        return
    