#----------------------------------------------------
# Mini BearTracks
# Purpose of program: Manage student timetables by enrolling in or dropping courses, and displaying the current timetable.
#
# Author: Hasan Khan
# Collaborators/references: https://www.w3schools.com/python/ref_string_ljust.asp
#----------------------------------------------------
from io import StringIO
import sys
import streamlit as st
import pandas as pd

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
    return st.sidebar.selectbox("Choose an action", 
                                ["Print Timetable", "Enroll in Course", "Drop Course", "Quit"])

def format_course(course_string):
    """Formats the course abbreviation code."""
    course_name, course_number = course_string.split()
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

    # Initialize enrolled_courses as an empty list
    enrolled_courses = []

    # Check which courses the student is enrolled in
    with open("enrollment.txt", "r") as f:
        for line in f:
            if ':' in line:  # Only proceed if colon exists in the line
                course_name, enrolled_student_id = map(str.strip, line.split(':'))
                if enrolled_student_id == student_id:
                    enrolled_courses.append(course_name)

    # Construct a timetable
    timetable = {}
    for course in enrolled_courses:
        if course not in courses_data:
            print(f"Warning: Course {course} not found in courses.txt. Skipping...")
            continue
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
    
    timetable_str = StringIO()
    old_stdout = sys.stdout
    sys.stdout = timetable_str

    # Prints header
    print(" " * 6, end='')
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
    sys.stdout = old_stdout
    timetable_formatted = timetable_str.getvalue()
    st.code(timetable_formatted, language='text')        
        
            
            

def get_valid_student(student_id_input):
    with open("students.txt", "r") as f:
        for line in f:
            parts = line.strip().split(',')
            if len(parts) >= 3:
                student_id = parts[0].strip()
                faculty = parts[1].strip()
                student_name = ','.join(parts[2:]).strip()
                if student_id_input == student_id:
                    return student_id, student_name
            
    st.error("Invalid student ID. Cannot continue with course enrollment.")
    return None, None

def get_valid_course(student_timetable, course_name_input):
    """
    Validates the course name and returns the course name and details if valid.
    """
    course_details = {}
    with open("courses.txt", "r") as f:
        for line in f:
            course_name, timeslot, max_students, lecturer = map(str.strip, line.split(';'))
            if course_name_input.upper() == course_name:
                course_details = {
                    "timeslot": timeslot,
                    "max_students": int(max_students),
                    "lecturer": lecturer
                }

    if not course_details:
        return None

    day_time = course_details["timeslot"].split()
    day_format = 'MWF' if 'MWF' in day_time[0] else 'TR'
    time = day_time[1]

    for existing_day, existing_courses in student_timetable.items():
        if day_format == existing_day:
            if time in existing_courses:
                st.warning(f"Schedule conflict: already registered for course on {day_format} {time}.")
                return None

    seat_count = sum(1 for line in open("enrollment.txt", "r") if course_name_input + ':' in line)
    if seat_count >= course_details["max_students"]:
        st.warning(f"Cannot enroll. {course_name_input} is already at capacity.")
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
    student_id_input = st.text_input("Student ID:")
    if student_id_input:
        student_id, student_name = get_valid_student(student_id_input)
        if student_id and student_name:
            st.write(f"Timetable for {student_name.upper()}")
            courses = generate_timetable(student_id)
            print_timetable(courses)
        else:
            st.error("Invalid student ID. Cannot print timetable.")

def option2():
    """Enrolls a student in a course."""
    st.subheader("Enroll in Course")
    
    student_id_input = st.text_input("Student ID")
    if student_id_input:
        student_id, student_name = get_valid_student(student_id_input)
        if student_id:
            st.success(f"Valid student ID for {student_name}")
            
            course_name_input = st.text_input("Course Name")
            if course_name_input:
                course_name_input = course_name_input.upper()  # Convert course name to uppercase
                student_timetable = generate_timetable(student_id)
                result = get_valid_course(student_timetable, course_name_input)
                if result:
                    course_name, course_details = result
                    if is_student_already_enrolled(student_id, course_name):
                        st.warning(f"{student_name} is already enrolled in {course_name}.")
                    else:
                        if st.button("Enroll"):
                            enroll_student_in_course(student_id, student_name, course_name, course_details)
                            st.success(f"{student_name} has successfully been enrolled in {course_name}.")
                else:
                    st.error("Invalid course name.")
        else:
            st.error("Invalid student ID. Cannot continue with course enrollment.")
            
def option3():
    """
    Handles the option '3' to drop a course for a student.
    """    
    student_id_input = st.text_input("Enter student ID for dropping a course:")
    
    if student_id_input:
        student_info = get_valid_student(student_id_input)
        if student_info:
            student_id, student_name = student_info
            enrolled_courses = []
            with open("enrollment.txt", "r") as f:
                for line in f:
                    if ':' in line:
                        course_name, enrolled_student_id = map(str.strip, line.split(':'))
                        if enrolled_student_id == student_id:
                            enrolled_courses.append(course_name)

            if not enrolled_courses:
                st.write(f"{student_name} is not enrolled in any courses.")
                return

            course_to_drop = st.selectbox("Select course to drop:", enrolled_courses)
            
            if st.button("Drop Course"):
                # Update the enrollment file
                with open("enrollment.txt", "r") as f:
                    lines = f.readlines()

                with open("enrollment.txt", "w") as f:
                    for line in lines:
                        if ':' in line:
                            course_name, enrolled_student_id = map(str.strip, line.split(':'))
                            if not (course_name == course_to_drop and enrolled_student_id == student_id):
                                f.write(line)

                st.success(f"{student_name} has successfully dropped {course_to_drop}.")
        else:
            st.error("Invalid student ID.")
def option4():
    st.subheader("Add New Student")
    
    student_id_input = st.text_input("Enter a new student ID (6 digits):")
    if student_id_input:
        if len(student_id_input) != 6 or not student_id_input.isdigit():
            st.error("Invalid student ID. Please enter a 6-digit number.")
        else:
            existing_ids = set()
            with open("students.txt", "r") as f:
                for line in f:
                    student_id = line.strip().split(",")[0]
                    existing_ids.add(student_id)
            
            if student_id_input in existing_ids:
                st.error("Student ID already exists. Please enter a unique ID.")
            else:
                faculty_options = ["BUS", "EDU", "ART", "SCI", "ENG"]
                faculty_input = st.selectbox("Select the faculty:", faculty_options)
                
                full_name_input = st.text_input("Enter the full name:")
                
                if st.button("Add Student"):
                    with open("students.txt", "a") as f:
                        f.write(f"\n{student_id_input},{faculty_input},{full_name_input}")
                    st.success("Student added successfully.")
def option5():
    st.subheader("Drop Out")
    
    student_id_input = st.text_input("Enter the student ID (CCID) to drop out:")
    if student_id_input:
        found = False
        updated_lines = []
        with open("students.txt", "r") as f:
            for line in f:
                student_id = line.strip().split(",")[0]
                if student_id == student_id_input:
                    found = True
                else:
                    updated_lines.append(line)
        
        if found:
            with open("students.txt", "w") as f:
                f.writelines(updated_lines)
            st.success(f"Student with CCID {student_id_input} has been dropped out.")
        else:
            st.warning(f"Student with CCID {student_id_input} not found.")
            
def main():
    st.title("Mini-BearTracks")
    st.header("Welcome to Mini-BearTracks")

    action = st.sidebar.selectbox("Choose an action", ["Print Timetable", "Enroll in Course", "Drop Course", "Add New Student", "Drop Out", "Quit"])

    if action == "Print Timetable":
        option1()
    elif action == "Enroll in Course":
        option2()
    elif action == "Drop Course":
        option3()
    elif action == "Add New Student":
        option4()
    elif action == "Drop Out":
        option5()
    elif action == "Quit":
        st.write("Goodbye")
        sys.exit()

if __name__ == "__main__":
    main()