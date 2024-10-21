import asyncio
import websockets
import json
import aiofiles

HA_URL = "ws://192.168.7.49:8123/api/websocket"
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJiODcwOTE3MTRmMDQ0YjZmOTI4MWM5OGY4OTc2OTQ4NSIsImlhdCI6MTcyOTM4MzQzNCwiZXhwIjoyMDQ0NzQzNDM0fQ.HqjF4wXkT9TmZkvJJT-kYep4cY8LASnvYjibGZmFp1Q"
PRESENCE_SENSOR_ID = "binary_sensor.esp32s3two_presence"


async def connect(callback, data):
    async with websockets.connect(HA_URL) as websocket:
        first_conn = await websocket.recv()

        # Send authentication token
        await websocket.send(json.dumps({
            "type": "auth",
            "access_token": TOKEN
        }))

        res = await websocket.recv()
        if (json.loads(res)['type'] != 'auth_ok'):
            return print(f"Error authenticating: {json.loads(res)}")

        print("Successfully authenticated with websocket server")

        # Send subscription request
        await websocket.send(json.dumps(data))

        while True:
            res = await websocket.recv()
            json_ = json.loads(res)

            # Use the callback function to handle the received data
            await callback(json_)