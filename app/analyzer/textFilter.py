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