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

def variableSetup(output):
    try:
        if output:
            output = output[0]

            boxes = [line[0] for line in output]
            txts = [line[1][0] for line in output]
            scores = [line[1][1] for line in output]

            return {"boxes": boxes, "txts": txts, "scores": scores}

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
        raw_names = filterdata(data['txts'])
        print('Filtering raw data',len(raw_names))
        return detectStudentNames(raw_names)
    
    except Exception as e:
        print(f"extractText error: {e}")
        return None