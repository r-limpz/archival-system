#!pip install pytesseract transformers ultralyticsplus ultralytics

import tensorflow as tf
import numpy as np
import pandas as pd
import re
import os
import cv2
from ultralyticsplus import YOLO, render_result
from PIL import Image
import pytesseract
from pytesseract import Output
from paddleocr import PaddleOCR, draw_ocr

image = './ROG_sample1.jpg'

img = Image.open(image)

# load model
model = YOLO('foduucom/table-detection-and-extraction')
# set model parameters
model.overrides['conf'] = 0.25  # NMS confidence threshold
model.overrides['iou'] = 0.8  # NMS IoU threshold
model.overrides['agnostic_nms'] = False  # NMS class-agnostic
model.overrides['max_det'] = 1000  # maximum number of detections per image
ocr = PaddleOCR(lang='en')


# perform inference
results = model.predict(img)

# observe results
render = render_result(model=model, image=img, result=results[0])

x1, y1, x2, y2, _, _ = tuple(int(item) for item in results[0].boxes.data.numpy()[0])
img = np.array(Image.open(image))
#cropping
cropped_image = img[y1:y2, x1:x2]
cropped_image = Image.fromarray(cropped_image)

im1 = cropped_image.save("yolo_crop.jpg") 

image_path = 'yolo_crop.jpg'
image_cv = cv2.imread(image_path)


image_height = image_cv.shape[0]
image_width = image_cv.shape[1]

#run an ocr 
output = ocr.ocr(image_path)

#text recognition
boxes = [line[0] for line in output]
texts = [line[1][0] for line in output]
scores = [line[1][1] for line in output]

im = image_cv.copy()

#text reonstruction
horiz_boxes =[]
vert_boxes = []

for box in boxes:
    x_h, x_v = 0, int(box[0][0]) #start at 0 for x-axis
    y_h, y_v = int(box[0][1]), 0  #end at 0 for y-axis
    width_h, width_v = image_width, int(box[2][0] - box[0][0])
    height_h, height_v =  int(box[2][1] - box[0][1]), image_height
    horiz_boxes.append([x_h, y_h, x_h+width_h, y_h+height_h])
    vert_boxes.append([x_v, y_v, x_v+width_v, y_v+width_v])

    cv2.rectangle(im,(x_h,y_h), (x_h+width_h, y_h+height_h),(255,0,0), 1) #horizontal
    cv2.rectangle(im,(x_v,y_v), (x_v+width_v, y_v+height_v),(0,255,0), 1) #vertical

#get horizontal boxes for table rows
horiz_out = tf.image.non_max_suppression( 
    horiz_boxes,
    scores,
    max_output_size = 1000,
    iou_threshold = 0.25, #intersection/union threshold to 
    score_threshold = float('-inf'), #infinite
    name = None
)
#sort the horizontal lines from array
horiz_lines = np.sort(np.array(horiz_out))

#get vertical boxes for table column
vert_out = tf.image.non_max_suppression( 
    vert_boxes,
    scores,
    max_output_size = 1000,
    iou_threshold = 0.25, #intersection/union threshold to 
    score_threshold = float('-inf'), #infinite
    name = None
)
#sort the vertical lines from array
vert_lines = np.sort(np.array(vert_out))

out_array = [["" for _ in range(len(vert_lines))] for _ in range(len(horiz_lines))]

def intersection(box_1, box_2):
    return[box_2[0], box_1[1], box_2[2], box_1[3]]

def iou(box_1, box_2):
    x_1 = max(box_1[0], box_2[0]) #ax1, bx1
    y_1 = max(box_1[1], box_2[1]) #ay1, by1
    x_2 = min(box_1[2], box_2[2]) #ax2, bx2
    y_2 = min(box_1[3], box_2[3]) #ay2, by2

    inter = abs(max((x_2 - x_1, 0)) * max((y_2 - y_1, 0)))
    if inter == 0:
        return 0

    box_1_area = abs((box_1[2] - box_1[0]) * (box_1[3] - box_1[1]))
    box_2_area = abs((box_2[2] - box_2[0]) * (box_2[3] - box_2[1]))

    return inter/ float( box_1_area + box_2_area - inter)

def getTableResult():
    dupl_box = []
    
    for i in range(len(horiz_lines)):
        for j in range(len(vert_lines)):
            resultant = intersection(horiz_boxes[horiz_lines[i]], vert_boxes[vert_lines[j]])

            for b in range(len(boxes)):
                the_box = [boxes[b][0][0],boxes[b][0][1],boxes[b][2][0],boxes[b][2][1]]
                if(iou(resultant, the_box) > 0.1):
                    if b not in dupl_box:
                        out_array[i][j] = texts[b]
    
    return out_array

def removeHeader(raw_names):
    header_items = [ 'report of rating', 'report', 'rating',
                        'surname first', 'surname', 'term', 
                        'final', 'grade', 'remarks', 'name in alphabetical order',
                        'remarks', 'mid-term', 'final-term', 'midterm'
                        ]
    
    empty_columns = [i for i, heading in enumerate(out_array[0]) if not heading] #detect empty table heading or duplicated columns

    for row in out_array:
        for index in sorted(empty_columns, reverse=True): 
            del row[index] 

    raw_names = [row[0] for row in out_array[1:] if row[0]]

    # Filter out rows that meet the condition
    filtered_raw_names = []

    for name in raw_names:
        # Normalize and convert name to lowercase for comparison
        normalized_name = re.sub(r'\s+', ' ', re.sub(r',', ' , ', re.sub(r'[^a-zA-ZÑñ-]', ' ', name))).strip().lower()
        
        # Check if normalized_name exists in header_lower
        if normalized_name not in header_items:
            filtered_raw_names.append(name)

    return filtered_raw_names

tableData = getTableResult()
raw_names = removeHeader(tableData)


