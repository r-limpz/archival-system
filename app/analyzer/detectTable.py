import numpy as np
from PIL import Image
from ultralyticsplus import YOLO

horiz_boxes =[]
vert_boxes = []

def CropTable(image, filename_crop):
    model = YOLO('foduucom/table-detection-and-extraction')

    # set model parameters
    model.overrides['conf'] = 0.25  # NMS confidence threshold
    model.overrides['iou'] = 0.8  # NMS IoU threshold
    model.overrides['agnostic_nms'] = False  # NMS class-agnostic
    model.overrides['max_det'] = 1000  # maximum number of detections per image

    img = Image.open(image)
    results = model.predict(img)

    # Check if any boxes were detected
    if len(results[0].boxes.data.numpy()) > 0:
        x1, y1, x2, y2, _, _ = tuple(int(item) for item in results[0].boxes.data.numpy()[0])
        img = np.array(Image.open(image))

        # Cropping
        cropped_image = img[y1:y2, x1:x2]
        cropped_image = Image.fromarray(cropped_image)
        file_path = "./app/analyzer/" + filename_crop
        
        try:
            cropped_image.save(file_path)
            return True
        
        except Exception as e:
            print("Error saving cropped image:", e)
            
    
    print("No table detected in the image.")
    return False
