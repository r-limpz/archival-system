import re

class StudentNames:
    def __init__(self, surname, firstname, middlename, suffix):
        self.surname = surname
        self.firstname = firstname
        self.middlename = middlename
        self.suffix = suffix

def removeUnwantedCharacters(raw_inputArray):
    filtered_studentNames = [
        re.sub(r'\s+', ' ', re.sub(r',', ' , ', re.sub(r'[^a-zA-ZÑñ.,]', ' ', rawText))).strip()
        for rawText in raw_inputArray
    ]
    updated_studentNames = []
    
    for name in filtered_studentNames:
        if name.startswith("."):
            name = name[1:]
            
        if ',' not in name and '.' in name:
            # Find the position of the period and check the length of the word after it
            name_parts = name.split('.')
            if len(name_parts[1]) > 2:
                name = name.replace('.', ',')
                
        if ',' not in name and '.' not in name:
            # Use a regex to insert commas before uppercase letters
            name = re.sub(r'(?<!^)(?=[A-Z])', ',', name)

        name = re.sub(r'\s+', ' ', re.sub(r',', ' , ', re.sub(r'[^a-zA-ZÑñ.,]', ' ', name))).strip().capitalize()
        updated_studentNames.append(name)
        
    return updated_studentNames

def isSuffixAndMiddleName(unstructured_ListOfSplitName):
    suffixList = ['jr.', 'sr.', 'i.', 'ii.', 'iii.', 'iv.', 'v.']
    data = {'middlename': '', 'middlename_index': -1, 'suffix': '', 'suffix_index': -1}
    for i, name in enumerate(unstructured_ListOfSplitName):
        if len(name) == 2 and name[1] == '.':
            data['middlename'] = name
            data['middlename_index'] = i
    for i in range(len(unstructured_ListOfSplitName)-1, -1, -1):
        if unstructured_ListOfSplitName[i] in suffixList and i != data['middlename_index']:
            data['suffix'] = unstructured_ListOfSplitName[i]
            data['suffix_index'] = i
    return data

def detectNameFormat(unstructured_nameformat):
    #setup the format and variables
    structured_nameformat = { 'surname': '', 'firstname': '', 'middlename': '', 'suffix': '' }
    array_name = unstructured_nameformat.split() #spli each by combination of characters/words
    nameData = isSuffixAndMiddleName(array_name) #run the function to get both middlename and suffix
    structured_nameformat['middlename'] = nameData.get('middlename').capitalize()# Add middleName
    middleNameIndex = nameData.get('middlename_index')
    structured_nameformat['suffix'] = nameData.get('suffix').upper()# Add suffix
    suffixIndex = nameData.get('suffix_index')
    temp_firstname = ''
    temp_surname = ''

    if not suffixIndex == -1: #after the suffix string value is stored remove it to the temporary list
        array_name = array_name[:suffixIndex] + array_name[suffixIndex+1:]
        
    #Determine if a comma is present to separate surname and firstname
    comma_index = array_name.index(',') if ',' in array_name else None

    if comma_index is not None: # f format is [ SURNAME* + ,+ FIRSTNAME* + M.I ]
        if not middleNameIndex == -1: #remove it since the structure doesn't relies on middlename location
            array_name = array_name[:middleNameIndex] + array_name[middleNameIndex+1:] #remove the middleName from the list
        
        temp_surname =  ' '.join(array_name[:comma_index]).title() #all list before comma is surname
        temp_firstname =  ' '.join(array_name[comma_index+1:]).title() #all list after comma is firstname
        
    else: #if format is [ FIRSTNAME* + M.I + SURNAME* ]
        if not middleNameIndex == -1 : #Has MiddleName
            if middleNameIndex == len(array_name):
                for i in range(len(array_name)-1, -1, -1):
                    if len(array_name[i]) > 1 and '.' not in array_name[i]:
                        temp_surname = array_name[i].upper()+'.'
                        array_name = array_name[:i] + array_name[i+1:]
                        break
                array_name = array_name[:middleNameIndex] + array_name[middleNameIndex+1:]
                temp_firstname = ' '.join(array_name[:len(array_name)-1])
            else:
                temp_firstname = ' '.join(array_name[:middleNameIndex]) #all list before middlename is firstname
                temp_surname = ' '.join(array_name[middleNameIndex+1:]) #all list after middlename is surname

            array_name = array_name[:middleNameIndex] + array_name[middleNameIndex+1:]
            
        else: # [FIRSTNAME* + SURNAME]
            for i in range(len(array_name)-1, -1, -1): #locate the middlename
                if len(array_name[i]) == 1:
                    structured_nameformat['middlename'] = array_name[i].upper()+'.'
                    break

            for i in range(len(array_name)-1, -1, -1):
                if len(array_name[i]) > 1 and '.' not in array_name[i]:
                    temp_surname = array_name[i].upper()+'.'
                    array_name = array_name[:i] + array_name[i+1:]
                    break

            temp_firstname = ' '.join(array_name[:len(array_name)-1])

    # add the values for the structured name format dictionary for surname and firstname
    structured_nameformat['surname'] = re.sub(r',', '', re.sub(r'[^a-zA-ZÑñ]', ' ', temp_surname)).title()
    structured_nameformat['firstname'] = re.sub(r',', '', re.sub(r'[^a-zA-ZÑñ.]', ' ', temp_firstname)).title()

    return structured_nameformat

def detectStudentNames(raw_data_string):
    StudentNamesList = []
    temp_studentList = []

    filteredData = removeUnwantedCharacters(raw_data_string)
    for input_name in filteredData:
        if input_name !='':
            name_result = detectNameFormat(input_name)
            student_data = StudentNames(**name_result)
            temp_studentList.append(student_data)
    
    for obj in temp_studentList: #append and remove redundancy
        if not obj.surname == '' and not obj.firstname == '' and not any(o.surname == obj.surname and o.firstname == obj.firstname and o.middlename == obj.middlename and o.suffix == obj.suffix for o in StudentNamesList):
            StudentNamesList.append(obj)
    
    return StudentNamesList