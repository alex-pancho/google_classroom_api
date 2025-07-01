from cr_students_api import Students

def add_students_to_classroom(course_id, file_path):
    """
    Invite students to a Google Classroom course.

    :param course_id: The ID of the course to which students will be added.
    :param file_path: The path to the file containing student email addresses.
    """
    # Create an instance of the Students class
    students = Students(course_id=course_id)

    # Read student emails from the file
    students.add_students_from_file(file_path)

if __name__ == "__main__":
    # Specify the course ID and the path to the student file
    course_id = 770249109796  # Replace with your actual course ID
    student_file_path = "students.csv"  # Path to the CSV file with student emails

    students = Students(course_id=course_id)
    current_students = students.get_students()
    print(f"Now course {course_id} has {len(current_students)} students")

    # Invite students to the course
    add_students_to_classroom(course_id, student_file_path)
    print(f"Students invited to course {course_id} from {student_file_path}.")