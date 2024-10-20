import cv2
import threading
import base64
from datetime import datetime
import numpy as np
from flask import Flask, request, jsonify, render_template_string
from flask_socketio import SocketIO, send, emit
from PIL import Image
from io import BytesIO
from modules import ai 
from modules import api
from modules import camera
from modules import websocket
import time
import re
import json
import asyncio
import logging
from werkzeug.serving import WSGIRequestHandler

werkzeug_logger = logging.getLogger('werkzeug')
werkzeug_logger.disabled = True

def b64_to_pil(img):
        img_data = base64.b64decode(img)
        np_arr = np.frombuffer(img_data, np.uint8)
        cv_image = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

        cv_image_rgb = cv2.cvtColor(cv_image, cv2.COLOR_BGR2RGB)
        return Image.fromarray(cv_image_rgb)

Cam = camera.new()

def log(user, action):
    curr = json.loads(open('logs.json', 'r').read() or '[]')

    curr.append({
        "user": user,
        "action": action,
        "timestamp": int(time.time())
    })

    new = json.dumps(curr)

    print(f"LOG [{user}] - {action}")
    open('logs.json', 'w').write(new)


def error_page(message, submessage):
    return (open('pages/error.html', 'r').read()).replace("{MESSAGEHERE}", message).replace("{SUBMESSAGEHERE}", submessage)
def get_real_ip(): 
    return request.headers.getlist("X-Forwarded-For")[0] or request.remote_addr
def check_ip(ip):
    file_path = 'auth/whitelist.json'

    try:
        with open(file_path, 'r') as file:
            whitelist = json.load(file)
    except Exception:
        whitelist = {}

    if ip in whitelist:
        return whitelist[ip] == True

    whitelist[ip] = False

    # Save the updated whitelist back to the JSON file
    with open(file_path, 'w') as file:
        json.dump(whitelist, file, indent=4)

    # Return False since the IP is new and set to "false"
    return False

def is_session_active(key):
    json_ = json.loads(open('auth/admin_sessions.json', 'r').read() or "{}")
    raw = open('auth/admin_sessions.json', 'r').read()

    if key not in raw: return False

    ts = json_[key]


    now = int(time.time())

    if (now - int(ts)) < 1800:
        return True
    else:
        return False
    
async def start_websocket():
    
    def callback_(json_):
        data = json.loads(open('events.json', 'r').read() or '[]') 

        found = False
        for i in range(len(data)):
            curr = data[i]
            try:
                if curr['event']['data']['new_state']['entity_id'] == json_['event']['data']['new_state']['entity_id']:

                    data[i] = json_
                    found = True
            except KeyError:
                continue
        if not found:
            data.append(json_)

        open('events.json', 'w').write(json.dumps(data))


        admin_socket.emit('broadcast_event', data)

    await websocket.connect(callback_)
    

lights_app = Flask(__name__)

inference_app = Flask(__name__)

admin_app = Flask(__name__)
admin_socket = SocketIO(admin_app)
@admin_socket.on('connect')
def on_connect():
    print("Client connected")
    emit('welcome', {'message': 'Welcome to the server!'})

@lights_app.before_request
def check_ip_whitelist():
    if not check_ip(get_real_ip()): 
        return error_page(f'ACCESS DENIED', f'Your IP: {get_real_ip()}'), 403
@lights_app.route('/toggle')
def toggle_lights():

    state_data = api.get_state_data('light.qhm_1cc9')
    current_state = state_data['state'] != 'off'
    method = "turn_off" if current_state else "turn_on"
    
    api.post_state('light', method, 'light.qhm_1cc9')
    img = Cam.capture_image()

    formatted_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    log(get_real_ip(), "Toggled lights")

    return jsonify({'state': not current_state, 'img': img, 'ts': str(formatted_timestamp)})
@lights_app.route('/')
async def lights():
    state_data = api.get_state_data('light.qhm_1cc9')
    current_state = state_data['state'] != 'off'


    return render_template_string((open('pages/lights.html', 'r').read()).replace("{}", str(current_state)))


@inference_app.before_request
def check_ip_whitelist():
    if not check_ip(get_real_ip()): 
        return error_page(f'ACCESS DENIED', f'Your IP: {get_real_ip()}'), 403
@inference_app.route('/')
def inference():
    return render_template_string(open('pages/inference.html', 'r').read())
@inference_app.route('/inference', methods=['POST'])
async def upload_file():
    log(get_real_ip(), "Uploaded file for inference.")

    result = []

    data = request.get_json()
    b64_img = data['image']
    decoded = base64.b64decode(b64_img)
    image_bytes = BytesIO(decoded)
    image = Image.open(image_bytes)

    safe_timestamp = str(int(time.time()))

    # Clean the IP address to remove invalid characters
    safe_ip = re.sub(r'[^a-zA-Z0-9_.-]', '_', str(get_real_ip()))

    # Save the image with a safe file name
    image.save(f'image_cache/{safe_timestamp}_{safe_ip}.png')

    cropped_images = await ai.detect_and_crop_objects(image)

    for img in cropped_images:
        predictions = ai.get_predictions(b64_to_pil(img))
        result.append({'predictions': predictions, 'img': img})

    if len(result) == 0:
         print("Couldn't find any objects, defaulting to search entire image")
         result.append({'predictions': ['No objects found.'], 'img': None})


    return jsonify(result)


@admin_app.route('/')
def admin():
    return render_template_string(open('pages/admin_auth.html', 'r').read())

@admin_app.route('/auth', methods=['POST'])
def auth():
    data = request.get_json()

    if data and data.get('password') == "bombie6376":
        curr = str(int(time.time()))
        key = data.get('key')

        data = json.loads(open('auth/admin_sessions.json', 'r').read() or "{}")
        
        data[key] = curr

        open('auth/admin_sessions.json', 'w').write(json.dumps(data))
        log(get_real_ip(), "Successfully authenticated in admin panel with password")

        return render_template_string(open('pages/admin.html', 'r').read())
    else:

        return render_template_string(error_page('Auth Error', 'Incorrect password'))
@admin_app.route('/auth_key', methods=['POST'])
def auth_key():
    data = request.get_json()
    key = data.get('key')

    if not key: return ''

    if is_session_active(key):
        log(get_real_ip(), "Successfully authenticated with session")
        return render_template_string(open('pages/admin.html', 'r').read()) 
    else:
        return ''
@admin_app.route('/logs', methods = ["POST"])
def logs():
    args = request.get_json()
    if (is_session_active(args.get('key'))):
        loaded = json.loads(open('logs.json', 'r').read() or "[]")
        return json.dumps(loaded)
    else:
        return ""
@admin_app.route('/save_whitelist', methods=['POST'])
def save():

    if (is_session_active(request.json.get('key'))):
        print("updating whitelist")

        ip = request.json.get('ip')
        state = request.json.get('state')

        json_ = json.loads(open('auth/whitelist.json', 'r').read()) or {}

        json_[ip] = state

        open('auth/whitelist.json', 'w').write(json.dumps(json_))

        if state == True: worded = "whitelisted"
        elif state == False: worded = "unwhitelisted"
        
        return f"Successfully {worded} {ip}!"
    else:
        return 403


def run_lights_app():
    lights_app.run(host="0.0.0.0", port=5000)

def run_inference_app():
    inference_app.run(host="0.0.0.0", port=6000)

def run_admin_app():
    admin_socket.run(app=admin_app, host='0.0.0.0', port=7000)

if __name__ == "__main__":
    log("Server", "Starting UP")

    threads = [
        threading.Thread(target=run_lights_app),
        threading.Thread(target=run_inference_app),
        threading.Thread(target=run_admin_app)
    ]
    
    for thread in threads:
        thread.start()

    asyncio.run(start_websocket())

    for thread in threads:
        thread.join()