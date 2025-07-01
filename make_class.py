from logger import logger
from classroom_api import CoursesCreation, Courses


def create_classroom():
    """
    Create a new Google Classroom course.
    """
    # Define course details
    course_details = dict(
        name="QA Automation with Python",
        section="Mon-Wed-Fri 19:10",
        room="Zoom",
        description_heading="Test Automation with Python",
        description=(
            "Complete program for QA automation specialists preparation.\n"
            "You'll gain skills in solving main automation testing tasks for web applications,\n"
            "learn architectural principles and build your own testing frameworks."
        ),
    )
    # Create the course
    CoursesCreation(**course_details)


def get_course_ids():
    """
    Get the IDs of the created courses.
    """
    course = Courses()
    return course()


if __name__ == "__main__":
    # create_classroom() 
    # # 770259944861
    # # 770249109796
    c_list = get_course_ids()
    for c in c_list:
        for k,v in c.items():
            logger.info(f"{k}: {v}")

    # You can add more functionality here, such as creating topics, adding students, etc.
    # For example:
    # topic = Topic(course_id=course)
    # topic.create("Week 1 - Introduction")
    # student = Student(course_id=course)
    # student.add("student@example.com")