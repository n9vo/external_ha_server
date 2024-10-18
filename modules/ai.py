import cv2
import numpy as np
import base64
from io import BytesIO
from PIL import Image
import asyncio
from ultralytics import YOLO


model = YOLO('models/yolov8s.pt')  

# Define the async function to detect and crop objects
async def detect_and_crop_objects(pil_image: Image.Image):
    # Convert the PIL Image to an OpenCV image
    open_cv_image = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
    height, width, channels = open_cv_image.shape

    # Load YOLO
    net = cv2.dnn.readNet("models/yolov3.weights", "models/yolov3.cfg")
    layer_names = net.getLayerNames()
    output_layers = [layer_names[i - 1] for i in net.getUnconnectedOutLayers()]

    # Prepare the image for YOLO
    blob = cv2.dnn.blobFromImage(open_cv_image, 0.00392, (416, 416), (0, 0, 0), True, crop=False)
    net.setInput(blob)

    # Perform the forward pass to get output asynchronously
    def forward_pass():
        return net.forward(output_layers)

    detections = await asyncio.to_thread(forward_pass)

    # Lists to hold details
    boxes = []
    confidences = []
    class_ids = []

    # Process YOLO detections
    for output in detections:
        for detection in output:
            scores = detection[5:]
            class_id = np.argmax(scores)
            confidence = scores[class_id]

            if confidence > 0.5:  # Threshold to keep good detections
                center_x = int(detection[0] * width)
                center_y = int(detection[1] * height)
                w = int(detection[2] * width)
                h = int(detection[3] * height)

                # Coordinates for the bounding box
                x = int(center_x - w / 2)
                y = int(center_y - h / 2)

                boxes.append([x, y, w, h])
                confidences.append(float(confidence))
                class_ids.append(class_id)

    # Apply Non-Maxima Suppression to avoid overlapping boxes
    indices = cv2.dnn.NMSBoxes(boxes, confidences, 0.5, 0.4)

    # Check if any boxes were found
    cropped_images_base64 = []
    if len(indices) > 0:
        for i in indices.flatten():  # Flatten to ensure it's iterable
            box = boxes[i]
            x, y, w, h = box
            
            # Ensure that the cropping coordinates are within the image dimensions
            x = max(0, x)
            y = max(0, y)
            w = min(w, width - x)
            h = min(h, height - y)

            # Perform the crop only if the dimensions are valid
            if w > 0 and h > 0:
                crop_img = open_cv_image[y:y+h, x:x+w]  # Crop the object from the original image
                
                # Convert the cropped image to base64
                is_success, buffer = cv2.imencode(".jpg", crop_img)
                
                # Check if encoding was successful
                if is_success:
                    io_buf = BytesIO(buffer)
                    encoded_cropped_img = base64.b64encode(io_buf.getvalue()).decode('utf-8')
                    cropped_images_base64.append(encoded_cropped_img)
                else:
                    print(f"Failed to encode image for box {box}")
            else:
                print(f"Invalid crop dimensions for box {box}")

    return cropped_images_base64

def get_predictions(img):
    """Get predictions from the YOLO model for the input image."""
    results = model(img)
    
    if isinstance(results, list):
        results = results[0]  

    labels = []

    if hasattr(results, 'names') and hasattr(results, 'boxes'):
        for box in results.boxes:
            label = results.names[int(box.cls)]
            labels.append(label)

    return labels if labels else ["No objects detected"]  