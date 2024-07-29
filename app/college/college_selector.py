from app.database import config 

class Colleges:
    def __init__(self, college_id, college_name, college_description, courses):
        self.college_id = college_id
        self.college_name = college_name
        self.college_description = college_description
        self.courses = courses

# function fetches a list of colleges from the database
def fetch_collegeList(search_college):
    if search_college:
        with config.conn.cursor() as cursor:
            #fetchall colleges in the database
            if search_college == 'all':
                cursor.execute('SELECT college_id, college_name, college_description FROM college WHERE 1=1')
                college_data = cursor.fetchall()
            else:
                college_id = int(search_college)
                cursor.execute('SELECT college_id, college_name, college_description FROM college WHERE college_id = %s', (college_id))
                college_data = cursor.fetchall()

            if college_data:
                return college_data
            else:
                return None
    else:
        return None
        
# function fetches the courses for each college and prepares the data for display
def fetch_course(search):
    college_list = fetch_collegeList(search) #utilize the fetch colleges function
    Col_Course_list = [] #list to store this data

    # Proceed if college list is not empty
    if college_list:
        with config.conn.cursor() as cursor: 
            # Iterate over each college
            for college_item in college_list:
                col_id = college_item.get('college_id')
                col_name = college_item.get('college_name')
                col_description = college_item.get('college_description')
                
                # Execute SQL query to fetch courses for the current college
                cursor.execute('SELECT course_id, course_name, course_description FROM courses WHERE registered_college =%s', (col_id))
                course_item = cursor.fetchall()
                courses = [] #temporary array storing courses data for each college

                # If courses data exists, format and store it
                if course_item: 
                    # Iterate the fetched list of courses
                    for entry in course_item:
                        #setup temporary dictionary storing course data
                        course_format = {'course_id' :"", 'course_name':""}  
                        course_format['course_id'] = entry['course_id']
                        course_format['course_name'] = entry['course_name']
                        course_format['course_description'] = entry['course_description']

                        #append the dictionary in the list
                        courses.append(course_format)
                # Create a new college object with fetched courses and append it to the list
                college = Colleges(col_id, col_name, col_description, courses)
                Col_Course_list.append(college)
                
        return Col_Course_list
    else:
        return None