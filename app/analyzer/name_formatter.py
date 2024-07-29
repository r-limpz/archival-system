import re
from app.analyzer.textFilter import removeUnwantedCharacters

class StudentNames:
    def __init__(self, surname, firstname, middlename, suffix):
        self.surname = surname
        self.firstname = firstname
        self.middlename = middlename
        self.suffix = suffix

def isSuffixAndMiddleName(unstructured_ListOfSplitName):
    #Determines and extracts suffix and middle name information from a list of split names.
    try:
        # List of common suffixes
        suffixList = ['jr.', 'sr.', 'i.', 'ii.', 'iii.', 'iv.', 'v.']
        # Initialize a dictionary to store results
        data = {'middlename': '', 'middlename_index': -1, 'suffix': '', 'suffix_index': -1}
        
        # Iterate through the list to find the middle name
        for i, name in enumerate(unstructured_ListOfSplitName):
            if len(name) == 2 and name[1] == '.':
                data['middlename'] = name
                data['middlename_index'] = i
        
        # Iterate through the list in reverse to find the suffix
        for i in range(len(unstructured_ListOfSplitName) - 1, -1, -1):
            if unstructured_ListOfSplitName[i] in suffixList and i != data['middlename_index']:
                data['suffix'] = unstructured_ListOfSplitName[i]
                data['suffix_index'] = i
        
        return data
    
    except Exception as e:
        # Print error message if an exception occurs
        print(f"MiddleName Selector Error: {e}")

def detectNameFormat(unstructured_nameformat):
    #define the dictionary format of student name
    structured_nameformat = {'surname': '', 'firstname': '', 'middlename': '', 'suffix': ''}
    array_name = unstructured_nameformat.split()
    nameData = isSuffixAndMiddleName(array_name)
    try:
        # Find and remove the middlename in the array name list
        if not nameData.get('middlename') == '':
            temp_middlename = re.sub(r'\W+', '', nameData.get('middlename')).upper()
            structured_nameformat['middlename'] = temp_middlename
            middleNameIndex = nameData.get('middlename_index')
            if not middleNameIndex == -1:
                array_name = array_name[:middleNameIndex] + array_name[middleNameIndex+1:]

        # Find and remove the sufffix in the array name list
        if not nameData.get('middlename') == '':
            temp_suffix = re.sub(r'\W+', '', nameData.get('suffix')).upper()
            structured_nameformat['suffix'] = temp_suffix
            suffixIndex = nameData.get('suffix_index')
            if not suffixIndex == -1:
                array_name = array_name[:suffixIndex] + array_name[suffixIndex+1:]

        #create an empty variables
        temp_firstname = ''
        temp_surname = ''

        #find the comma to determine the remaining name parts
        comma_index = array_name.index(',') if ',' in array_name else None
        #if comma exist the format is [surname][comma][firstname]
        if comma_index is not None:
            temp_surname = ' '.join(array_name[:comma_index])
            temp_firstname = ' '.join(array_name[comma_index+1:])

        #if comma not exist the format is [surname][period or null][firstname]
        else:
            #find the period in thee array name
            period_index = array_name.index('.') if '.' in array_name else None
            if period_index is not None:
                if (len(array_name[:period_index].strip()) > 2 and len(array_name[period_index + 1:].strip()) > 2):
                    temp_surname = ' '.join(array_name[:period_index])
                    temp_firstname = ' '.join(array_name[period_index + 1:])
            #if name has "dela" that exist use it as 1st word in a surname
            if "Dela" in array_name:
                dela_index = array_name.index("Dela")
                temp_surname = ' '.join(array_name[:dela_index])
                temp_firstname = ' '.join(array_name[dela_index + 1:])
            #last condition is to get the surname as 1st element in the list
            else:
                temp_surname = array_name[0].title()
                temp_firstname = ' '.join(array_name[1:])

        temp_surname = re.sub(r'[^A-Za-z]', ' ', temp_surname)  # Replace non-alphabetic characters with spaces
        temp_surname = re.sub(r'\s+', ' ', temp_surname).strip()  # Replace multiple spaces with single space and strip leading/trailing spaces
        temp_firstname = re.sub(r'[^A-Za-z\.]', ' ', temp_firstname)  # Replace non-alphabetic and non-dot characters with spaces
        temp_firstname = re.sub(r'\s+', ' ', temp_firstname).strip()  # Replace multiple spaces with single space and strip leading/trailing spaces

        structured_nameformat['surname'] = temp_surname.title()
        structured_nameformat['firstname'] = temp_firstname.title()

        if not structured_nameformat['surname'] == '' and not structured_nameformat['firstname'] == '':
            return structured_nameformat
        
    except Exception as e:
        print(f"detectNameFormat Error: {e}")
        return None

def detectStudentNames(raw_data_string):
    StudentNamesList = []
    temp_studentList = []

    try:
        #remove unwanted characters on each entries in the raw_data_string list
        filteredData = removeUnwantedCharacters(raw_data_string)
        
        #iterate the filteredData to populate student list
        for input_name in filteredData:
            #only accept non empty elements
            if input_name != '':
                #generate a dictionary of name foramt from raw string
                name_result = detectNameFormat(input_name)
                if name_result:
                    #Using the class creating an object to append on the temp list
                    student_data = StudentNames(**name_result)
                    temp_studentList.append(student_data)

        #iterate the temp list to remove elements with empty surname and firstname (reject invalid names entries)
        for obj in temp_studentList:
            if obj.surname != '' and obj.firstname != '' and not any(o.surname == obj.surname and o.firstname == obj.firstname and o.middlename == obj.middlename and o.suffix == obj.suffix for o in StudentNamesList):
                StudentNamesList.append(obj)

        print('Filtered Entries: ',len(filteredData))
        return StudentNamesList
    except Exception as e:
        print(f"detectStudentNames Error: {e}")

    