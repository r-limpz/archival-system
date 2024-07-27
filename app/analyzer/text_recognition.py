from paddleocr import PaddleOCR
import numpy as np
import pandas as pd
import os
import re
from app.analyzer.name_formatter import detectStudentNames
from app.analyzer.textFilter import filterdata

def analyzerText(filepath):
    try:
        ModelOCR = PaddleOCR(lang='en')
        result = ModelOCR.ocr(filepath)
        if result:
            return result  # Return the OCR result as a dictionary
        else:
            return None  # Return a placeholder if no result
        
    except Exception as e:
        print('analyzerText Error: ',e)

def header_removal(output):
    try:
        if output:
            boxes = [line[0] for line in output]
            txts = [line[1][0] for line in output]
            scores = [line[1][1] for line in output]

            print('raw :', len(txts))

            header_items = [
                'report of rating', 'name in alphabetical order', 'report', 'rating',
                'mid-term', 'midterm', 'mid term', 'final-term', 'finalterm', 'final term',
                'finalgrade', 'final-grade', 'final grade', 'remarks', 'remark',
                'surename first', 'surename', '(surename)'
            ]

            # Convert header items to lower case for case insensitive comparison
            header_items_lower = [header.lower() for header in header_items]
            indices_to_delete = []
            # Iterate through txts to identify and mark lines containing headers
            for i in range(len(txts)):
                if txts[i]:
                    cleaned_txt = re.sub(r'\s+', ' ', re.sub(r',', ' , ', re.sub(r'[^a-zA-ZÑñ\s]', ' ', txts[i]))).strip().lower()
                    # Check if cleaned_txt contains any header item
                    if cleaned_txt in header_items_lower:
                        indices_to_delete.append(i)

            # Delete items from the lists in reverse order to avoid index errors
            for idx in reversed(indices_to_delete):
                del boxes[idx]
                del txts[idx]
                del scores[idx]

            print('new :', len(txts))
            return {"boxes": boxes, "txts": txts, "scores": scores}
        
    except Exception as e:
        print('header_removal Error: ', e)

def variableSetup(output):
    try:
        if output:
            output = output[0]
            return header_removal(output)

    except Exception as e:
        print(f"variableSetup Error: {e}")
        return None

def extractText(file):
    image_path = "./app/analyzer/temp.jpg"
    file.save(image_path)

    script_dir = os.path.dirname(os.path.abspath(__file__))
    file_directory = os.path.join(script_dir, "temp.jpg")

    try:
        output = analyzerText(file_directory)
        data = variableSetup(output)
        raw_names = filterdata(data['txts'],'1d')
        print('Filtering raw data',len(raw_names))
        return detectStudentNames(raw_names)
    
    except Exception as e:
        print(f"extractText error: {e}")
        return None