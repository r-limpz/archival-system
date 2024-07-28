from app.benchmark.accuracyChecker import checkMissingData
import numpy as np
import pandas as pd
import os

def createCSV(data, filename):
    try:
        script_dir = os.path.dirname(__file__)  # Directory of the current script
        file_path = os.path.join(script_dir, filename)
        
        df = pd.DataFrame(data)
        df.to_csv(file_path, index=False)
        return file_path
    except Exception as e:
        print(f"Error creating CSV file: {e}")
        return None

def fetchCSV(filename):
    try:
        script_dir = os.path.dirname(__file__)  # Directory of the current script
        file_path = os.path.join(script_dir, filename)
        
        df = pd.read_csv(file_path)
        return df
    except Exception as e:
        print(f"Error fetching CSV file: {e}")
        return None

def updateCSV(WER_data, CER_data, filename):
    try:
        script_dir = os.path.dirname(__file__)  # Directory of the current script
        file_path = os.path.join(script_dir, filename)
        
        # Fetch the existing CSV data
        df = fetchCSV(file_path)
        
        # Prepare the new data to append or update
        new_data = {
            'date': pd.Timestamp.now(),
            'Average_WER': WER_data,
            'Average_CER': CER_data
        }
        
        # Append the new data to the existing dataframe or create a new one if df is None
        if df is not None:
            df = df.append(new_data, ignore_index=True)
        else:
            df = pd.DataFrame([new_data])

        # Write back to CSV
        df.to_csv(file_path, index=False)
        
        return True
    except Exception as e:
        print(f"Error updating CSV file: {e}")
        return False

def getAccuracy(corrected_data, ocr_data, filename):
    try:
        script_dir = os.path.dirname(__file__)  # Directory of the current script
        file_path = os.path.join(script_dir, filename)
        
        if filename:
            if os.path.exists(file_path):
                return updateCSV(corrected_data,ocr_data, filename)
            else:
                print(f"CSV file '{filename}' does not exist.")
                return False
        return False
    except Exception as e:
        print(f"Error getting accuracy: {e}")
        return False
