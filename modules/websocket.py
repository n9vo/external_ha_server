import asyncio
import websockets
import json


HA_URL = "ws://192.168.7.49:8123/api/websocket"
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJiODcwOTE3MTRmMDQ0YjZmOTI4MWM5OGY4OTc2OTQ4NSIsImlhdCI6MTcyOTM4MzQzNCwiZXhwIjoyMDQ0NzQzNDM0fQ.HqjF4wXkT9TmZkvJJT-kYep4cY8LASnvYjibGZmFp1Q"
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
        return print(f"Error authenticating: {json.loads(res)}")
    
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

