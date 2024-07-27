import re

def removeUnwantedCharacters(raw_inputArray):
    filtered_studentNames = [
        re.sub(r'\s+', ' ', re.sub(r',', ' , ', re.sub(r'[^a-zA-ZÑñ.,]', ' ', rawText))).strip()
        for rawText in raw_inputArray
    ]
    updated_studentNames = []
    
    for name in filtered_studentNames:
        if name.startswith("."):
            name = name[1:]

        # Insert a comma before uppercase letters if no comma is found
        if ',' not in name:
            name = re.sub(r'(?<!^)(?<!\s)(?=[A-Z])', ',', name)
        
        # Replace periods with commas if both the character before and after the period have length >= 3
        if '.' in name:
            name_parts = name.split('.')
            if len(name_parts) > 1 and len(name_parts[0]) >= 3 and len(name_parts[1]) >= 3:
                name = name.replace('.', ',')

        # Final cleanup: remove unwanted characters, replace multiple spaces with single space, and title case
        name = re.sub(r'\s+', ' ', re.sub(r',', ' , ', re.sub(r'[^a-zA-ZÑñ.,]', ' ', name))).strip().title()
        updated_studentNames.append(name)
        
    return updated_studentNames

def pattern_valid(data):
    # Check if the string starts with a comma
    if re.match(r'^,', data):
        return False

    # Check if the string has a number between non-digit characters
    if re.search(r'\D\d\D', data):
        return False
    
    # Remove all commas and dots from the data
    cleaned_data = re.sub(r'[,.]', '', data)
    cleaned_data = re.sub(r'[^A-Za-z]', '', cleaned_data)

    arr = re.split(r'(?<!^)(?=[A-Z])', cleaned_data)
    arr = [elem for elem in arr if elem]

    # If arr length is less than 2 elements, return False
    if len(arr) < 2:
        return False
    # If arr has exactly 2 elements, check if any element has 1 character length
    if len(arr) == 2:
        if any(len(elem) == 1 for elem in arr):
            return False
    # If arr has more than 2 elements, check if the first element has 1 character length
    elif len(arr) > 2:
        if len(arr[0]) == 1:
            return False

    return True

def isvalidEntry(entries):
    # Define patterns to filter entries
    studentList =[]

    for entry in entries:
            # Append the entry if it does not match the invalid pattern or matches the valid pattern
            if pattern_valid(entry):
                studentList.append(entry)
    
    if len(studentList) > 0:
        return studentList

    return None

def filterdata(out_array):
    try:
        # Define header items, grades, and remarks
        header_items = [
            'report of rating', 'name in alphabetical order', 'report', 'rating',
            'mid-term', 'midterm', 'mid term', 'final-term', 'finalterm', 'final term',
            'finalgrade', 'final-grade', 'final grade', 'remarks', 'remark',
            'surename first', 'surename'
        ]
        grades = ['1.0', '1.25', '1.5', '1.75', '2.0', '2.25', '2.5', '2.75', '3.0', 'inc']
        remarks = ['pass', 'passed', 'fail', 'inc', 'failed',
                   'no grades', 'dropped', 'dropped.', 'no final exam', 'no final exam.', 'exam', 'no exam', 'final',
                   'no requirement', 'no requirements']
        
        # Initialize temporary list for filtered data
        tempList = []
        entries = []

        # Process each item in the out_array
        if len(out_array) > 0:
            for name in out_array:
                if name:
                    # Normalize and convert name to lowercase for comparison
                    item = re.sub(r'\s+', ' ', name).strip().lower()

                    if item not in [header for header in header_items]:
                        if item in grades or item in remarks:
                            tempList.append("")
                        else:
                            tempList.append(name)

            # Concatenate adjacent items from tempList into entries
            for i in range(len(tempList)):
                current = tempList[i]

                if current:
                    # Concatenate with the next element if within bounds and not empty
                    if i < len(tempList) - 1 and tempList[i + 1]:
                        name = current + " " + tempList[i + 1]
                        if name not in entries:
                            entries.append(name)
                        
                    # Add the current item itself if it's not empty and not added before
                    elif current not in entries:
                        entries.append(current)
        
        print('Processing raw data',len(entries))
        return isvalidEntry(entries)

    except Exception as e:
        print(f"An error occurred: {e}")
        return None
