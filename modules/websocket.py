import asyncio
import websockets
import json
import aiofiles
import json

ip = json.load(open('../config.json', 'r'))['ha_ip']
token = json.load(open('../config.json', 'r'))['ha_token']

HA_URL = "ws://" + ip + ":8123/api/websocket"
TOKEN = token

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
