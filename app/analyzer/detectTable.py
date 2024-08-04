import numpy as np
from PIL import Image
from ultralyticsplus import YOLO 

def make_white_background(image):
    # If image has an alpha channel (transparency), convert it to white background
    if image.mode == 'RGBA':
        background = Image.new('RGB', image.size, (255, 255, 255))
        background.paste(image, mask=image.split()[3])  # 3 is the alpha channel
        return background
    else:
        return image.convert('RGB')

def CropTable(image, filename_crop):
    file_path = "./app/analyzer/" + filename_crop  # creating the directory
    model = YOLO('foduucom/table-detection-and-extraction')  # Initializing YOLO model with specific weights

    # Setting model parameters for object detection
    model.overrides['conf'] = 0.25  # Confidence threshold for non-maximum suppression (NMS)
    model.overrides['iou'] = 0.8  # Intersection over Union (IoU) threshold for NMS
    model.overrides['agnostic_nms'] = False  # Setting NMS to class-aware (not class-agnostic)
    model.overrides['max_det'] = 1000  # Maximum number of detections per image

    img = Image.open(image)
    img = make_white_background(img)  # Ensure image has white background if it originally had transparency

    results = model.predict(img)  # Execute object detection on the image using the YOLO model

    if len(results[0].boxes.data.numpy()) > 0:
        # Extracting coordinates of the first detected bounding box
        x1, y1, x2, y2, _, _ = tuple(int(item) for item in results[0].boxes.data.numpy()[0])
        img_array = np.array(img)  # Convert the image to a numpy array for processing

        # Cropping the image based on the detected bounding box data
        cropped_image = img_array[y1:y2, x1:x2]  # Cropping the image using numpy slicing
        cropped_image = Image.fromarray(cropped_image)  # Converting the cropped numpy array back to PIL Image

        try:
            cropped_image.save(file_path)  # save the cropped image
            return True  # True indicates successful cropping
        
        except Exception as e:
            print("Error saving cropped image:", e)
            
    print("No table detected in the image.") 
    return False
