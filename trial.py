import re

StudentNamesList = []
class student_names:
    def __init__ (self, surname, firstname, middlename, suffix):
        self.surname = surname
        self.firstname = firstname 
        self.middlename = middlename
        self.suffix = suffix

def removeUnwantedCharacters(raw_inputArray):
    filtered_studentNames = [re.sub(r'\s+', ' ', re.sub(r',', ' , ', re.sub(r'[^a-zA-ZÑñ.,]', ' ', rawText))).strip().lower() for rawText in raw_inputArray]
    return filtered_studentNames 

def isSuffixAndMiddleName(unstructured_ListOfSplitName):
    suffixList = ['jr.', 'sr.','i.' ,'ii.', 'iii.', 'iv.','v.']
    data = { 'middlename':'', 'middlename_index':-1 ,'suffix': '', 'suffix_index': -1,}

    for i, name in enumerate(unstructured_ListOfSplitName): #locate the middlename first
        if len(name) == 2 and name[1] == '.': #middlename must be 2 characters which '.' is mandatory
            data['middlename'] = name
            data['middlename_index'] = i

    for i in range(len(unstructured_ListOfSplitName)-1, -1, -1): #locate the suffix based on the suffList
        if unstructured_ListOfSplitName[i] in suffixList and i != data['middlename_index']: #not same with middlename index
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

def detectStudentNames(RawDataString):
    temp_studentList = []
    filteredData = removeUnwantedCharacters(RawDataString)

    for input_name in filteredData: #Format the input data
        name_result = detectNameFormat(input_name)
        student_data = student_names(**name_result)
        temp_studentList.append(student_data)
    
    for obj in temp_studentList: #append and remove redundancy
        if not any(o.surname == obj.surname and o.firstname == obj.firstname and o.middlename == obj.middlename and o.suffix == obj.suffix for o in StudentNamesList):
            StudentNamesList.append(obj)

def displayNameObjects(StudentNamesList):
    for student in StudentNamesList:
        print(f"Surname: {student.surname} \nFirstname: {student.firstname} \nMiddlename: {student.middlename} \nSuffix: {student.suffix} \n")

RawInput = [
    " Moe Jhester V.  Kha jr." ,
    "  Jhonson , Lester  M." ,
    "_$%//Damian-- ,--Reymond-Ferdinand V." ,
    " 01823737__&&%^$$Ymir----, -309 Lester=93287272--moe I. V." ,
    "Carrillo ,Luisito Mayra II. A." ,
    "Sastre, Eloy Paula V. I." ,
    "Santana, Harutyun Blanca A." ,
    "Montero, Eligia Mikayela N. Ma." ,
    "Martin Otilia Borja Ma. Jr. A."
]

detectStudentNames(RawInput)
displayNameObjects(StudentNamesList)
