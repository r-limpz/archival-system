import re
from app.analyzer.textFilter import removeUnwantedCharacters

class StudentNames:
    def __init__(self, surname, firstname, middlename, suffix):
        self.surname = surname
        self.firstname = firstname
        self.middlename = middlename
        self.suffix = suffix

def isSuffixAndMiddleName(unstructured_ListOfSplitName):
    try:
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
    
    except Exception as e:
        print(f" MiddleName Selector Error: {e}")

def detectNameFormat(unstructured_nameformat):
    structured_nameformat = {'surname': '', 'firstname': '', 'middlename': '', 'suffix': ''}
    array_name = unstructured_nameformat.split()
    nameData = isSuffixAndMiddleName(array_name)
    try:
        structured_nameformat['middlename'] = nameData.get('middlename').capitalize()
        middleNameIndex = nameData.get('middlename_index')
        structured_nameformat['suffix'] = nameData.get('suffix').upper()
        suffixIndex = nameData.get('suffix_index')
        temp_firstname = ''
        temp_surname = ''

        if not suffixIndex == -1: #after the suffix string value is stored remove it to the temporary list
            array_name = array_name[:suffixIndex] + array_name[suffixIndex+1:]

        if middleNameIndex != -1:
            array_name = array_name[:middleNameIndex] + array_name[middleNameIndex+1:]

        comma_index = array_name.index(',') if ',' in array_name else None

        if comma_index is not None:
            temp_surname = ' '.join(array_name[:comma_index])
            temp_firstname = ' '.join(array_name[comma_index+1:])

        else:
            period_index = array_name.index('.') if '.' in array_name else None
            if period_index is not None:
                if (len(array_name[:period_index].strip()) > 2 and len(array_name[period_index + 1:].strip()) > 2):
                    temp_surname = ' '.join(array_name[:period_index])
                    temp_firstname = ' '.join(array_name[period_index + 1:])

            if "Dela" in array_name:
                dela_index = array_name.index("Dela")
                temp_surname = ' '.join(array_name[:dela_index])
                temp_firstname = ' '.join(array_name[dela_index + 1:])
            else:
                temp_surname = array_name[0].title()
                temp_firstname = ' '.join(array_name[1:])

        structured_nameformat['surname'] = re.sub(r',', '', temp_surname).title().strip() 
        structured_nameformat['firstname'] = re.sub(r',', '', temp_firstname).title().strip()

        return structured_nameformat
    except Exception as e:
        print(f"detectNameFormat Error: {e}")
        return None

def detectStudentNames(raw_data_string):
    StudentNamesList = []
    temp_studentList = []

    try:
        filteredData = removeUnwantedCharacters(raw_data_string)
        
        for input_name in filteredData:
            if input_name != '':
                name_result = detectNameFormat(input_name)
                student_data = StudentNames(**name_result)
                temp_studentList.append(student_data)

        for obj in temp_studentList:
            if obj.surname != '' and obj.firstname != '' and not any(o.surname == obj.surname and o.firstname == obj.firstname and o.middlename == obj.middlename and o.suffix == obj.suffix for o in StudentNamesList):
                StudentNamesList.append(obj)

        print('Filtered Entries: ',len(filteredData))
    except Exception as e:
        print(f"detectStudentNames Error: {e}")

    return StudentNamesList