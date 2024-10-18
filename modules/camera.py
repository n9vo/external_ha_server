import threading, cv2, base64
class new:

    def __init__(self):
        self.lock = threading.Lock()

    def capture_image(self):
        with self.lock:
            video = cv2.VideoCapture(2)
            success, image = video.read()
            video.release()

            if success:
                ret, jpeg = cv2.imencode('.jpg', image)
                if ret:
                    jpeg_base64 = base64.b64encode(jpeg).decode('utf-8')
                    return jpeg_base64
            return None

