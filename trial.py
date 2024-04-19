import re
class student_names:
    def __init__ (self, surname, firstname, middlename, suffix):
        self.surname = surname
        self.firstname = firstname 
        self.middlename = middlename
        self.suffix = suffix

def removeUnwantedCharacters(raw_inputArray):
    filtered_studentNames = []
    for rawText in raw_inputArray:
        filterString = re.sub(r'[^a-zA-ZÑñ.,]', ' ', rawText) # Save only alphabet characters, ".", and ","
        filterString = re.sub(r',', ' , ', filterString)
        filterString = re.sub(r'\s+', ' ', filterString).strip()# Remove double spaces
        filtered_studentNames.append(filterString)

    return filtered_studentNames

def detectNameFormat(unstructured_nameformat):
    #setup the format and variables
    suffixList = ['Jr.', 'Sr.', 'II.', 'III.', 'IV.', 'V.', 'VI']
    structured_nameformat = { "surname": "", "firstname": "", "middlename": "", "suffix": "" }
    array_name = unstructured_nameformat.split()

    # Check if the last element is a suffix and update accordingly
    if array_name[-1] in suffixList:
        structured_nameformat["suffix"] = array_name[-1]
        array_name = array_name[:-1]

    # Locate for middle name indicated by a period 
    for i in range(len(array_name)-1, -1, -1):
        if len(array_name[i]) == 2 and array_name[i][1] == '.':
            structured_nameformat["middlename"] = array_name[i]
            array_name = array_name[:i] + array_name[i+1:]
            break  # exit the loop once the first single character + '.' is found

    # Determine if a comma is present to separate surname and firstname
    comma_index = array_name.index(',') if ',' in array_name else None 

    if comma_index is not None:
        # Process names with a comma, separating surname and firstname
        temp_surname = ' '.join(array_name[:comma_index])
        structured_nameformat['surname'] = re.sub(r'[^a-zA-ZÑñ]', ' ', temp_surname)
        temp_firstname = ' '.join(array_name[comma_index+1:])
        structured_nameformat['firstname'] = re.sub(r'[^a-zA-ZÑñ.]', ' ', temp_firstname)
    else:
        # If no comma, treat the entire name as firstname
       
        for i in range(len(array_name)-1, -1, -1):
            if not array_name[i].endswith('.'):
                temp_surname = re.sub(r',', '', array_name[i])
                structured_nameformat['surname'] = temp_surname
                array_name = array_name[:i] + array_name[i+1:]
                break

        temp_firstname = ' '.join(array_name)
        structured_nameformat['firstname'] = re.sub(r',', '', temp_firstname)
    
    return structured_nameformat

def detectStudentNames(RawDataString):
    temp_studentList = []
    filteredData = removeUnwantedCharacters(RawDataString)

    for input_name in filteredData: 
        # Format the input data
        name_result = detectNameFormat(input_name)
        student_data = student_names(**name_result)
        temp_studentList.append(student_data)

    for obj in temp_studentList:
        if not any(o.surname == obj.surname and o.firstname == obj.firstname and o.middlename == obj.middlename and o.suffix == obj.suffix for o in StudentNamesList):
            StudentNamesList.append(obj)
     

RawInput =  ["01823737__&&%^$$Moe----, -309 Lester=93287272-Kha", " Moe Jhonson , Lester  ", "_$%//Damian--Elinor001,--Reymond-Ferdinand210192MA.-10928A.@@@#11#23V.", "01823737__&&%^$$Ymir----, -309 Lester=93287272--moe"]
newRawInput =  ["01823737__&&%^$$Andrew-Bruh---D. -309 Hoelster=Niqqers", " Moe Lester MA. Jr. "]

StudentNamesList = []

detectStudentNames(RawInput)
detectStudentNames(newRawInput)

for student in StudentNamesList:
    print(f"Surname: {student.surname} \nFirstname: {student.firstname} \nMiddlename: {student.middlename} \nSuffix: {student.suffix} \n")