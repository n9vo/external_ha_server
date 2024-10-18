import asyncio
import websockets
import json


HA_URL = "ws://192.168.7.49:8123/api/websocket"
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiI3ZjUyNzdmZTliM2M0ODY2YjkyNTA5ODViMzk4OWRiZSIsImlhdCI6MTcyOTA0NTY0MCwiZXhwIjoyMDQ0NDA1NjQwfQ.-67y0JjE6-2PP4daJnsO4AafUxAG9rfNv8kC6Ieu9Yc"
PRESENCE_SENSOR_ID = "binary_sensor.esp32s3two_presence"

async def connect(callback):
    websocket = await websockets.connect(HA_URL)

    first_conn = await websocket.recv()

    await websocket.send(json.dumps({
        "type": "auth",
        "access_token": TOKEN
    }))

    res = await websocket.recv()
    if (json.loads(res)['type'] != 'auth_ok'):
        return print("Error authenticating")
    
    print("Successfully authenticated with websocket server")

    await websocket.send(json.dumps({
        "id": 6000,
        "type": "subscribe_events",
        "event_type": "state_changed"
    }))

    while True:
        res = await websocket.recv()
        json_ = json.loads(res)

        callback(json_)

