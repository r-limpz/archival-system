import numpy as np
from PIL import Image
from ultralyticsplus import YOLO

import numpy as np
from PIL import Image

def convert_to_rgb(img):
    try:
        # If the image is already in RGB mode, return it directly
        if img.mode == 'RGB':
            print('Matrix : RGB')
            return img

        # Convert image to RGBA if it has an alpha channel
        if img.mode == 'RGBA':
            print('Matrix : RGBA')
            # Convert the image to a NumPy array
            img_array = np.array(img)
            
            # Split into RGB and Alpha channels
            rgb_array, alpha_channel = img_array[:, :, :3], img_array[:, :, 3]

            # Create a white background
            white_background = np.ones_like(rgb_array) * 255

            # Composite the image onto the white background based on the alpha channel
            alpha_factor = alpha_channel[:, :, np.newaxis] / 255.0
            composite = rgb_array * alpha_factor + white_background * (1 - alpha_factor)
            composite = composite.astype(np.uint8)

            # Convert back to a PIL Image and return it
            return Image.fromarray(composite, 'RGB')

        # Convert other modes directly to RGB
        rgb_image = img.convert('RGB')
        return rgb_image
    
    except Exception as e:
        print("Error converting image to RGB format:", e)
        return None


def CropTable(image, filename_crop):
    model = YOLO('foduucom/table-detection-and-extraction')

    # Set model parameters
    model.overrides['conf'] = 0.25  # NMS confidence threshold
    model.overrides['iou'] = 0.8  # NMS IoU threshold
    model.overrides['agnostic_nms'] = False  # NMS class-agnostic
    model.overrides['max_det'] = 1000  # Maximum number of detections per image

    try:
        img = Image.open(image)
    except Exception as e:
        print("Error opening image file:", e)
        return False

    try:
        results = model.predict(img)
    except Exception as e:
        print("Error predicting with the model:", e)
        return False

    # Check if any boxes were detected
    if len(results[0].boxes.data.numpy()) > 0:
        try:
            x1, y1, x2, y2, _, _ = tuple(int(item) for item in results[0].boxes.data.numpy()[0])
        except Exception as e:
            print("Error processing detection results:", e)
            return False

        try:
            rgb_img = convert_to_rgb(Image.open(image))
            img = np.array(rgb_img)

            # Cropping
            cropped_image = img[y1:y2, x1:x2]
            cropped_image = Image.fromarray(cropped_image)
            file_path = "./app/analyzer/" + filename_crop
            
            cropped_image.save(file_path)
            return True
        except Exception as e:
            print("Error processing and saving cropped image:", e)
            return False
    else:
        print("No table detected in the image.")
        return False
