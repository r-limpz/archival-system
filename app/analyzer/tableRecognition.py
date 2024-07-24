import cv2
import os
import tensorflow as tf
from paddleocr import PaddleOCR, draw_ocr
import numpy as np
from app.analyzer.name_formatter import detectStudentNames
from app.analyzer.resultChecker import displayResult

def file_manager(image_path):
    image_cv = cv2.imread(image_path)
    return image_cv

def analyzerText(filepath):
    try:
        ModelOCR = PaddleOCR(lang='en')
        result = ModelOCR.ocr(filepath)
        if result:
            return result  # Return the OCR result as a dictionary
        else:
            return None  # Return a placeholder if no result
        
    except Exception as e:
        print('analyzerText data Error: ',e)
    
def variableSetup(output):
    if output:
        output = output[0]

        boxes = [line[0] for line in output]
        txts = [line[1][0] for line in output]
        scores = [line[1][1] for line in output]

        return {"boxes": boxes,"txts": txts, "scores":scores}
    return None

def layoutAnalyzer(image_cv, boxes, image_height, image_width):
    im = image_cv.copy()
    horiz_boxes =[]
    vert_boxes = []

    for box in boxes:
        x_h, x_v = 0, int(box[0][0]) #start at 0 for x-axis
        y_h, y_v = int(box[0][1]), 0  #end at 0 for y-axis
        width_h, width_v = image_width, int(box[2][0] - box[0][0])
        height_h, height_v =  int(box[2][1] - box[0][1]), image_height
        
        horiz_boxes.append([x_h, y_h, x_h+width_h, y_h+height_h])
        vert_boxes.append([x_v, y_v, x_v+width_v, y_v+width_v])
    
    if horiz_boxes and vert_boxes:
        return {"horiz_boxes": horiz_boxes,"vert_boxes": vert_boxes}
    return None

def rowsDetector(horiz_boxes, scores):
    horiz_out = tf.image.non_max_suppression( 
        horiz_boxes,
        scores,
        max_output_size = 1000,
        iou_threshold = 0.35,
        score_threshold = float('-inf'),
        name = None
    )

    return horiz_out # Convert to list before returning

def columnDetector(vert_boxes, scores):
    vert_out = tf.image.non_max_suppression( 
        vert_boxes,
        scores,
        max_output_size = 1000,
        iou_threshold = 0.25,
        score_threshold = float('-inf'),
        name = None
    )
    
    return vert_out #Convert to list before returning

def setupBoxOrder(vert_lines, vert_boxes):

    unordered_boxes = []
    for i in vert_lines:
        print(vert_boxes[i])
        unordered_boxes.append(vert_boxes[i][0])

    print(np.argsort(unordered_boxes))
    return np.argsort(unordered_boxes)

def intersection(box_1, box_2):
    return[box_2[0], box_1[1], box_2[2], box_1[3]]

def iou(box_1, box_2):
    if box_1 and box_2:
        x_1 = max(box_1[0], box_2[0])
        y_1 = max(box_1[1], box_2[1])
        x_2 = min(box_1[2], box_2[2])
        y_2 = min(box_1[3], box_2[3])

        inter = abs(max((x_2 - x_1, 0)) * max((y_2 - y_1, 0)))
        if inter == 0:
            return 0

        box_1_area = abs((box_1[2] - box_1[0]) * (box_1[3] - box_1[1]))
        box_2_area = abs((box_2[2] - box_2[0]) * (box_2[3] - box_2[1]))

        return inter/ float( box_1_area + box_2_area - inter)
    return None

def fetchStudentList(out_array):
    empty_columns = [i for i, heading in enumerate(out_array[0]) if not heading] #detect empty table heading or duplicated columns

    for row in out_array:
        for index in sorted(empty_columns, reverse=True): 
            del row[index] #delete determine column index for each rows

    raw_names = [row[0] for row in out_array[1:] if row[0]]

    if raw_names:
        students = detectStudentNames(raw_names)
        return students
    return None

def tableDataAnalyzer(image_path = "yolo_crop.jpg"):
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        file_directory = os.path.join(script_dir, image_path)

        if os.path.exists(file_directory):
            
            image_cv = cv2.imread(file_directory)
            output = analyzerText(file_directory)

            image_height = image_cv.shape[0]
            image_width = image_cv.shape[1] 
            dupl_box = []

            if output:
                boxes = variableSetup(output)["boxes"]
                txts = variableSetup(output)["txts"]
                scores = variableSetup(output)["scores"]

                layout = layoutAnalyzer(image_cv, boxes, image_height, image_width)

                if layout:
                    horiz_boxes = layout['horiz_boxes']
                    vert_boxes = layout['vert_boxes']
                    horiz_out = rowsDetector(horiz_boxes, scores)
                    vert_out = columnDetector(vert_boxes, scores)
                    horiz_lines = np.sort(np.array(horiz_out))
                    vert_lines = np.sort(np.array(vert_out))

                    out_array = [["" for i in range(len(vert_lines))] for j in range(len(horiz_lines))]

                    for i in range(len(horiz_lines)):
                        for j in range(len(vert_lines)):
                            resultant = intersection(horiz_boxes[horiz_lines[i]], vert_boxes[vert_lines[j]])

                            for b in range(len(boxes)):
                                the_box = [boxes[b][0][0],boxes[b][0][1],boxes[b][2][0],boxes[b][2][1]]
                                if(iou(resultant, the_box) > 0.1):
                                    if b not in dupl_box:
                                        out_array[i][j] = txts[b]
                
                    if out_array:
                        return fetchStudentList(out_array)
        return None

    except Exception as e:
        print('tableDataAnalyzer data Error: ',e)  # Return a dictionary with the error message
