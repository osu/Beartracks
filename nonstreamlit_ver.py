#----------------------------------------------------
# Purpose of program: Manage student timetables by enrolling in or dropping courses, and displaying the current timetable.
#
# Author: Hasan Khan
# Collaborators/references: https://www.w3schools.com/python/ref_string_ljust.asp
#----------------------------------------------------

def welcome_to_beartracks():
    """
    Print a welcome message for Mini-BearTracks.
    
    Inputs: None
    
    Returns: None
    """
    print("==========================")
    print("Welcome to Mini-BearTracks")
    print("==========================")    

def getAction():
    """
    Prompt the user with possible actions and obtain their choice.
    
    Returns: 
        str: The user's selected action ('1', '2', '3', or '4') or invalid entry.
    """
    menu_options = "\nWhat would you like to do?\n1. Print timetable\n2. Enroll in course\n3. Drop course\n4. Quit"
    print(menu_options)    
    action = input("> ")
    while action not in ['1', '2', '3', '4']:
        print("Sorry, invalid entry. Please enter a choice from 1 to 4.")
        action = input("> ")
    return action

def format_course(course_string):
    """
    Formats the course abbreviation code.
    
    Inputs: course_string (str): A course in the form "STAT 151"
    
    Returns: str: Formatted course name where long course names are truncated with an asterisk.
    """    
    course_name, course_number = course_string.split()  # Splits "CMPUT 175" into "CMPUT" and "175"
    
    if len(course_name) > 4:
        formatted_name = course_name[:3] + "*"
    else:
        formatted_name = course_name
        
    return f"{formatted_name} {course_number}"

def generate_timetable(student_id):
    """
    Generates the timetable for the inputted student (doesnt print).
    
    Inputs: student_id (str): ID of the student.
    
    Returns: dict: Timetable dictionary made for the inputted student.
    """
    # Store courses in a dictionary with course name as key and its details as values
    courses_data = {}
    with open("courses.txt", "r") as f:
        for line in f:
            course_name, timeslot, max_students, lecturer = map(str.strip, line.split(';'))
            courses_data[course_name] = {"timeslot": timeslot, "max_students": int(max_students), "lecturer": lecturer}

    # Check which courses the student is enrolled in
    enrolled_courses = []
    with open("enrollment.txt", "r") as f:
        for line in f:
            if ':' in line:  # Only proceed if colon exists in the line
                course_name, enrolled_student_id = map(str.strip, line.split(':'))
                if enrolled_student_id == student_id:
                    enrolled_courses.append(course_name)

    # Construct a timetable
    timetable = {}
    for course in enrolled_courses:
        day_time = courses_data[course]["timeslot"].split()
        day = 'MWF' if 'MWF' in day_time[0] else 'TR' 
        time = day_time[1]    

        # Calculates seat count for the specified course
        seat_count = sum(1 for line in open("enrollment.txt") if course + ':' in line)

        # Calculates the number of open seats for the current course
        open_seats = courses_data[course]["max_students"] - seat_count

        if day not in timetable:
            timetable[day] = {}
        timetable[day][time] = {"course": course, "room": open_seats}  # Use open_seats instead of max_students

    return timetable



def print_timetable(courses):
    """
    Print the timetable in a structured format.
    
    Inputs: courses (dict): Dictionary of the courses.
    
    Returns: None
    """    
    headers = ['Mon', 'Tues', 'Wed', 'Thurs', 'Fri']
    day_codes = ['MWF', 'TR', 'MWF', 'TR', 'MWF']
    times = ['8:00', '8:30', '9:00', '9:30', '10:00', '10:30', '11:00', '11:30', 
             '12:00', '12:30', '13:00', '13:30', '14:00', '14:30', '15:00', '15:30', '16:00', '16:30']

    # Prints header
    print(" " * 5, end='')
    for day in headers:
        print(" "+f"{day.center(12)}", end='')
    print("\n" + " " * 5 + "+" + "+".join(["-" * 12 for _ in headers]) + "+")

    # Printing for each time
    for time in times:
        # Print course names for this time
        print(time.ljust(5) + "|", end='')  
        for i, day in enumerate(day_codes):
            if courses.get(day, {}).get(time):
                course = format_course(courses[day][time]['course'])
                print(f"{course.center(12)}|", end='')
            else:
                print(" " * 12 + "|", end='')
        print()

        # Print open seat counts for this time
        print(" " * 5 + "|", end='') 
        for i, day in enumerate(day_codes):
            if courses.get(day, {}).get(time):
                room = str(courses[day][time]['room'])
                print(f"{room.center(12)}|", end='')
            else:
                print(" " * 12 + "|", end='')
        text = "\n" + " " * 5
        if times.index(time) % 6 == 5:
            text += "+"
        else:
            text += "|"
        for _ in headers:
            if _ == "Mon" or _ == "Wed" or _ == "Fri":
                if times.index(time) % 2 == 1:
                    text += "-" * 12
                else:
                    text += " " * 12
            else:
                if times.index(time) % 3 == 2:
                    text += "-" * 12
                else:
                    text += " " * 12
            if times.index(time) % 6 == 5:
                text += "+"
            else:
                text += "|"
                    
        print(text)

def get_valid_student():
    """
    Prompts the user for a student ID and validates it otherwise asks for it again.
    
    Inputs: None
    
    Returns: tuple: student ID and student name if valid, otherwise (None, None).
    """    
    student_id_input = input(f"\nStudent ID: ").strip()
    with open("students.txt", "r") as f:
        for line in f:
            student_id, faculty, student_name = map(str.strip, line.split(',')) # This maps the str.strip on each element of the list to remove any whitespace infront/behind of str
            if student_id_input == student_id:
                return student_id, student_name
    print("Invalid student ID. Cannot continue with course enrollment.")
    return None, None

def get_valid_course(student_timetable):
    """
    Prompt the user for a course name and validate it against the student's current timetable.
    
    Inputs: student_timetable (dict): The student's current timetable.
    
    Returns: tuple: The course name and its details if valid, otherwise None.
    """
    course_details = {}
    course_name_input = input("Course name: ").strip().upper()
    with open("courses.txt", "r") as f:
        for line in f:
            course_name, timeslot, max_students, lecturer = map(str.strip, line.split(';')) 
            if course_name_input == course_name:
                course_details = {
                    "timeslot": timeslot,
                    "max_students": int(max_students),
                    "lecturer": lecturer
                }

    # Check validity of course
    if not course_details:
        print("Invalid course name.")
        return None

    # Check time conflicts between enrolled courses

    day_time = course_details["timeslot"].split()
    day_format = 'MWF' if 'MWF' in day_time[0] else 'TR'
    time = day_time[1]
    
    for existing_day, existing_courses in student_timetable.items():
        if day_format == existing_day:  # If the days match (like if both are MWF)
            if time in existing_courses:  # If there's already an enrolled course at that time
                print(f"Schedule conflict: already registered for course on {day_format} {time}.")
                return None
    

    # Check seat availability
    seat_count = 0
    with open("enrollment.txt", "r") as f:
        for line in f:
            if ':' in line:  # Only process if colon exists in the line
                course_name_in_file, _ = map(str.strip, line.split(':'))
                if course_name_input == course_name_in_file:
                    seat_count += 1

    if seat_count >= course_details["max_students"]:
        print(f"Cannot enroll. {course_name_input} is already at capacity. Please contact advisor to get on waiting list..")
        return None

    return course_name_input, course_details


def enroll_student_in_course(student_id, student_name, course_name, course_details):
    """
    Enroll a student in a course and update the file.
    
    Inputs: student_id (str): ID of the student.
            student_name (str): Name of the student.
            course_name (str): Name of the course.
            course_details (dict): Details of the course.
    
    Returns:
        None
    """    
    with open("enrollment.txt", "a") as f:
        f.write(f"\n{course_name}: {student_id}")
    day_time = course_details["timeslot"].split()
    day = 'MWF' if 'MWF' in day_time[0] else 'TR'
    time = day_time[1]    
    
    print(f"{student_name} has successfully been enrolled in {course_name}, on {day} {time}")
    
def is_student_already_enrolled(student_id, course_name):
    """
    Checks if a student is already enrolled in a particular course.
    
    Inputs: student_id (str): ID of the student
    course_name (str): Course name.
    
    Returns: bool: True if the student is already enrolled, False otherwise.
    """
    with open("enrollment.txt", "r") as f:
        for line in f:
            if ':' in line:
                course_name_in_file, student_id_in_file = map(str.strip, line.split(':'))
                if course_name_in_file == course_name and student_id_in_file == student_id:
                    return True
    return False

    
def option1():
    """
    Handle the option '1' to print a student's timetable.
    
    Inputs: None
    
    Returns: None
    """    

    student_id_input = input(f"\nStudent ID: ").strip()
    
    with open("students.txt", "r") as e:
        for line in e:
            parts = line.split(',')
            student_id = parts[0].strip()
            faculty = parts[1].strip()
            student_name = parts[2].strip()
            
            if student_id_input == student_id:
                print(f"Timetable for {student_name.upper()}, in the faculty of {faculty}")
                courses = generate_timetable(student_id_input)
                print_timetable(courses)
                return
            
    print("Invalid student ID. Cannot print timetable.") 
    

    
def option2():
    """
    Handles the option '2' to enroll a course for a student.
    
    Inputs: None
    
    Returns: None
    """        
    student_id, student_name = get_valid_student()
    if not student_id:
        return
    student_timetable = generate_timetable(student_id)
    result = get_valid_course(student_timetable)
    if not result:  # check if result is None
        return
    course_name, course_details = result  # unpack the result if it's not None
    if is_student_already_enrolled(student_id, course_name):
        print(f"\n{student_name} is already enrolled in {course_name}.")
        return
    enroll_student_in_course(student_id, student_name, course_name, course_details)

def option3():
    """
    Handles the option '3' to drop a course for a student.
    
    Inputs: None
    
    Returns: None
    """    
    student_id, student_name = get_valid_student()
    if not student_id:
        return

    # Get the courses the student is enrolled in
    enrolled_courses = []
    with open("enrollment.txt", "r") as f:
        for line in f:
            if ':' in line:  # Only process if colon exists in the line
                course_name, enrolled_student_id = map(str.strip, line.split(':'))
                if enrolled_student_id == student_id:
                    enrolled_courses.append(course_name)

    # Display courses the student is enrolled in
    if not enrolled_courses:
        print(f"\n{student_name} is not enrolled in any courses.")
        return

    print(f"Select course to drop:")
    for course in sorted(enrolled_courses):
        print(f"- {course}")

    # Ask user which course to drop
    course_to_drop = input("> ").strip().upper()
    if course_to_drop not in enrolled_courses:
        print(f"Drop failed. {student_name} is not currently registered in {course_to_drop}.")
        return

    # Update the enrollment file
    with open("enrollment.txt", "r") as f:
        lines = f.readlines()

    with open("enrollment.txt", "w") as f:
        for line in lines:
            if ':' in line:  # Check if the line has a colon before splitting it
                course_name, enrolled_student_id = map(str.strip, line.split(':'))
                if not (course_name == course_to_drop and enrolled_student_id == student_id):
                    f.write(line)

    print(f"\n{student_name} has successfully dropped {course_to_drop}.")


def main():
    # Call the welcome_to_beartracks function to print the welcome message
    welcome_to_beartracks()

    while True:
        action = getAction()
        if action == "1":
            option1()
        elif action == "2":
            option2()
        elif action == "3":
            option3()
        elif action == "4":
            print("Goodbye")
            exit()

if __name__ == "__main__":
    main()
    