import re
import pandas as pd

def removeUnwantedCharacters(raw_inputArray):
    updated_studentNames = []
    
    for name in raw_inputArray:
        cleaned_name = re.sub(r'[^a-zA-ZÑñ.,]', ' ', name) # Remove unwanted characters and normalize punctuation
        cleaned_name = re.sub(r'\.{2,}', '.', cleaned_name)  # Normalize multiple periods to a single period
        cleaned_name = re.sub(r',{2,}', ',', cleaned_name)  # Normalize multiple commas to a single comma
        cleaned_name = cleaned_name.strip() # Remove leading and trailing spaces

        # Remove leading periods before an uppercase letter
        if cleaned_name.startswith("."):
            cleaned_name = cleaned_name[1:]
        # Remove leading periods before an uppercase letter
        if cleaned_name.startswith(","):
            cleaned_name = cleaned_name[1:]
        
        # If no comma is found, find the nearest period to convert
        if ',' not in cleaned_name:
            # Find the last period to potentially convert to comma
            period_index = cleaned_name.rfind('.')
            if period_index != -1:
                # Check if the word after the period is not less than 3 characters
                next_word_start = period_index + 1
                next_space_index = cleaned_name.find(' ', next_word_start)
                if next_space_index != -1:
                    next_word = cleaned_name[next_word_start:next_space_index]
                else:
                    next_word = cleaned_name[next_word_start:]
                
                if len(next_word) >= 3:
                    cleaned_name = cleaned_name[:period_index] + ',' + cleaned_name[period_index + 1:]

        cleaned_name = re.sub(r'([A-Z])', r' \1', cleaned_name) # Add single space after every Uppercase
        cleaned_name = re.sub(r',', ' , ', cleaned_name) # Replace commas with space-comma-space
        cleaned_name = re.sub(r'\.', '. ', cleaned_name) # Replace periods with space-period-space
        cleaned_name = re.sub(r'\s+', ' ', cleaned_name) # Replace multiple spaces with single space 
        cleaned_name = cleaned_name.title() # Title case the cleaned name
        
        updated_studentNames.append(cleaned_name)
    return updated_studentNames

def redundancyRemoval(row):
    df = pd.DataFrame({'col': row})
    # using drop_duplicates() method
    df.drop_duplicates(inplace=True)
    # converting back to list
    return df['col'].tolist()

def filterdata(out_array):
    try:
        # Define header items, grades, and remarks
        header_items = [
            'report of rating', 'name in alphabetical order', 'report', 'rating',
            'mid-term', 'midterm', 'mid term', 'final-term', 'finalterm', 'final term',
            'finalgrade', 'final-grade', 'final grade', 'remarks', 'remark',
            'surename first', 'surename', '(surename)', 'surname', 'surname first', '(surname)'
        ]
        grades = ['1.0', '1.25', '1.5', '1.75', '2.0', '2.25', '2.5', '2.75', '3.0', 'inc']
        remarks = ['pass', 'passed', 'fail', 'inc', 'failed',
                   'no grades', 'dropped', 'dropped.', 'no final exam', 'no final exam.', 'exam', 'no exam', 'final',
                   'no requirement', 'no requirements']

        if out_array:
            entries = []

            for row in out_array:
                filtered_row = []
                newData = redundancyRemoval(row)
                for i in range(len(newData)):
                    item = re.sub(r'\s+', ' ', newData[i]).strip().lower()
                    # Check if both columns are not in grades or remarks
                    if item not in grades and item not in remarks:
                        # If there are two different columns, join them as the name
                        filtered_row.append(newData[i])

                joined_row = ' '.join(filtered_row)
                entries.append(joined_row)
                
            print('No# of Entries: ',len(out_array))
            print('Processing Entries: ',len(entries))

            return entries

    except Exception as e:
        print(f"An error occurred: {e}")
        return None
