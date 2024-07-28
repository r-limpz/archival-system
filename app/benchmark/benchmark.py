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
        
        if filename:
            if os.path.exists(file_path):
                df = fetchCSV(file_path)
                
                # Prepare the new data to append or update
                new_data = {
                    'date': pd.Timestamp.now(),
                    'Average_WER': WER_data,
                    'Average_CER': CER_data
                }
                
                if df is not None:
                    df = df.append(new_data, ignore_index=True)
                else:
                    df = pd.DataFrame([new_data])

                df.to_csv(file_path, index=False)
                return True
            else:
                print(f"CSV file '{filename}' does not exist.")
        
        return False
    except Exception as e:
        print(f"Error updating CSV file: {e}")

