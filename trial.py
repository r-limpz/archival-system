import re

def filter_input_data(input_data):
    filtered_data = re.sub(r'[^a-zA-Z.,]', ' ', input_data) # Save only alphabet characters, ".", and ","
    filtered_data = re.sub(r'\s+', ' ', filtered_data)# Remove double spaces
    
    return filtered_data.strip()

def format_input_namedata(name):
    #setup the format and variables
    suffixList = ['Jr.', 'Sr.', 'i', 'ii', 'iii', 'iv', 'v', 'vi']
    name_format = { "surname": "", "firstname": "", "middleName": "", "suffix": "" }
    temp_name = name.split()

    # Check if the last element is a suffix and update accordingly  
    if temp_name[-1] in suffixList:
        name_format["suffix"] = temp_name[-1]
        temp_name = temp_name[:-1]

    # Check for middle name indicated by a period in the last element
    if '.' in temp_name[-1]:
        name_format["middleName"] = temp_name[-1]
        temp_name = temp_name[:-1]
    
    # Determine if a comma is present to separate surname and firstname
    comma_index = temp_name.index(',') if ',' in temp_name else None

    if comma_index is not None:
        # Process names with a comma, separating surname and firstname
        name_format['surname'] = ' '.join(temp_name[:comma_index])
        name_format['firstname'] = ' '.join(temp_name[comma_index+1:])
    else:
        # If no comma, treat the entire name as firstname
        name_format['firstname'] = ' '.join(temp_name)

    return name_format

inputdata = "_$%//Damian--Elinor001,--Reymond-Ferdinand210192-10928A.@@@#11#23%Jr."
filtered_data = filter_input_data(inputdata)
student_name = format_input_namedata(filtered_data)

print('\n\nOrginal Input:      ', inputdata)
print('After Filtering:    ',filtered_data)
print('Final Output:       ',student_name)

