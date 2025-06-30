"""
Google Classroom Manager - Enhanced system for working with Google Classroom API
"""
import codecs
import io
import sys
import logging

from dataclasses import dataclass, asdict
from pathlib import Path
from typing import List, Dict, Optional
from tempfile import NamedTemporaryFile

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.errors import HttpError
from googleapiclient.discovery import build

from fileprocessor import read_csv_json_file, write_csv_json_file


SCOPES = [
    "https://www.googleapis.com/auth/classroom.rosters",
    "https://www.googleapis.com/auth/classroom.courses",
    "https://www.googleapis.com/auth/classroom.coursework.students",
    "https://www.googleapis.com/auth/classroom.courseworkmaterials",
    "https://www.googleapis.com/auth/classroom.topics",
    "https://www.googleapis.com/auth/classroom.announcements",
    "https://www.googleapis.com/auth/calendar",
]

# Override stdout and stderr to support UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")
utf8_stdout = codecs.getwriter("utf-8")(sys.stdout.buffer, "strict")
file_handler = logging.FileHandler("google_class.log", encoding="utf8")

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[file_handler, logging.StreamHandler(utf8_stdout)],
)
logger = logging.getLogger(__name__)


def authenticate():
    creds = False
    my_dir = Path(__file__).parent
    token_file = my_dir / "token.json"
    credentials_file = my_dir / "client_secret.json"
    # Авторизація користувача
    if token_file.exists():
        creds = Credentials.from_authorized_user_file(token_file, SCOPES)
    if not creds or creds.expired:
        logger.info("Refreshing tokens...")
        if not credentials_file.exists():
            raise FileNotFoundError(f"Credentials file not found: {credentials_file}")

        flow = InstalledAppFlow.from_client_secrets_file(str(credentials_file), SCOPES)
        creds = flow.run_local_server(port=0)

        # Save tokens
        with open(token_file, "w") as token:
            token.write(creds.to_json())
    logger.info("Tokens saved")
    return creds


class GoogleClassroomBuild:

    def __init__(self):
        self.creds = authenticate()
        self.build_services()

    def build_services(self) -> None:
        """Build Google API services"""
        try:
            self.classroom_service = build(
                "classroom", "v1", credentials=self.creds
            ).courses()
            self.calendar_service = build(
                "calendar", "v3", credentials=self.creds
            )
            logger.info("✅ Services connected")
        except Exception as e:
            logger.error(f"❌ Error connecting to services: {e}")
            raise


class Courses(GoogleClassroomBuild):

    def __init__(self, course_id_or_name):
        """
        Initialize Google Classroom Courses manager

        Args:
            course_id_or_name: Course id (int) or name(str)
        """
        super().__init__()
        self.get_courses()
        if isinstance(course_id_or_name, str):
            self.get_course_by_name(course_id_or_name)
        elif isinstance(course_id_or_name, int):
            self.get_course_by_id(course_id_or_name)
        else:
            raise ValueError("Invalid course identifier type")

    def get_courses(self) -> List[Dict]:
        """Get list of all courses"""
        try:
            response = self.classroom_service.list(courseStates=["ACTIVE"]).execute()
            courses = response.get("courses", [])
            logger.info(f"📚 Found courses: {len(courses)}")
            self.courses = courses
        except HttpError as e:
            logger.error(f"❌ HTTP error getting courses: {e}")
            return []
        except Exception as e:
            logger.error(f"❌ Error getting courses: {e}")
            return []

    def get_course_by_name(self, course_name: str) -> Optional[str]:
        """
        Find course ID by name

        Args:
            course_name: Course name

        Returns:
            Course ID or None
        """
        for course in self.courses:
            if course.get("name", "").lower() == course_name.lower():
                logger.info(
                    f"✅ Course: {course['name']} was foud and set as default (ID: {course['id']})"
                )
                self.course_id = course["id"]
                return course["id"]

        logger.warning(f"⚠️ Course '{course_name}' not found")
        return None

    def get_course_by_id(self, course_id: str) -> Optional[str]:
        """
        Find course ID by name

        Args:
            course_id: Course name

        Returns:
            Course ID or None
        """
        for course in self.courses:
            if str(course.get("id", "")) == str(course_id):
                logger.info(
                    f"✅ Course: {course['name']} was foud and set as default (ID: {course['id']})"
                )
                self.course_id = course["id"]
                return course["id"]

        logger.warning(f"⚠️ Course '{course_id}' not found")
        return None


class CoursesCreation(GoogleClassroomBuild):

    def __init__(self, name, **kwargs):
        """
        Create new course

        Args:
            name: Course name
            section: Section
            room: Room
            description: Description
            description_heading: Description heading

        Returns:
            Created course ID or None
        """
        super().__init__()
        self.create_course(name, **kwargs)

    def __call__(self):
        try:
            return self.course_id
        except AttributeError:
            logger.error("❌ Course ID not set. Please call create_course first.")
            return None

    def create_course(
        self,
        name: str,
        section: str = "",
        room: str = "",
        description: str = "",
        description_heading: str = "",
    ) -> Optional[str]:
        """
        Create new course

        Args:
            name: Course name
            section: Section
            room: Room
            description: Description
            description_heading: Description heading

        Returns:
            Created course ID or None
        """
        course_data = {
            "name": name,
            "section": section,
            "room": room,
            "description": description,
            "descriptionHeading": description_heading,
            "ownerId": "me",
        }

        try:
            course = self.classroom_service.create(body=course_data).execute()
            logger.info(f"✅ Course created: {name} (ID: {course['id']})")
            self.course_id = course["id"]
            return course["id"]

        except HttpError as e:
            logger.error(f"❌ HTTP error creating course: {e}")
            return None
        except Exception as e:
            logger.error(f"❌ Error creating course: {e}")
            return None


class Students(GoogleClassroomBuild):

    def __init__(self, course_id):
        super().__init__()
        self.course_id = course_id

    def add_student(self, student_email: str) -> bool:
        """
        Add student to course

        Args:
            course_id: Course ID
            student_email: Student email

        Returns:
            True if successful, False otherwise
        """
        try:
            student_data = {"userId": student_email}

            response = (
                self.classroom_service.students()
                .create(courseId=self.course_id, body=student_data)
                .execute()
            )

            student_name = (
                response.get("profile", {})
                .get("name", {})
                .get("fullName", student_email)
            )
            logger.info(f"✅ Student added: {student_name}")
            return True

        except HttpError as e:
            if e.resp.status == 409:
                logger.warning(f"⚠️ Student {student_email} already in course")
            else:
                logger.error(f"❌ HTTP error adding student: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ Error adding student: {e}")
            return False

    def add_students_from_file(self, file_path: str) -> Dict[str, int]:
        """
        Add students from file (CSV or JSON)

        Args:
            course_id: Course ID
            file_path: Path to file with students

        Returns:
            Addition statistics
        """
        stats = {"added": 0, "failed": 0, "already_exists": 0}

        students = read_csv_json_file(file_path)
        if not students or students is None:
            logger.warning("⚠️ No valid students found")
            return stats
        logger.info(f"📖 Reading {len(students)} students from file")

        # Add each student
        for student in students:
            email = (
                student.get("email")
                or student.get("Email")
                    or student.get("student_email")
                )

            if not email:
                logger.warning(f"⚠️ No email found for student: {student}")
                stats["failed"] += 1
                continue

            if self.add_student(email):
                stats["added"] += 1
            else:
                if "already in course" in str(student):
                    stats["already_exists"] += 1
                else:
                    stats["failed"] += 1

        logger.info(
            f"📊 Results: {stats['added']} added, {stats['already_exists']} already exist, {stats['failed']} failed"
        )
        return stats

    def get_students(self) -> List[Dict]:
        """
        Get list of students in course

        Args:
            course_id: Course ID

        Returns:
            List of students
        """
        try:
            students = []
            page_token = None

            while True:
                response = (
                    self.classroom_service.students()
                    .list(courseId=self.course_id, pageToken=page_token, pageSize=100)
                    .execute()
                )

                students.extend(response.get("students", []))
                page_token = response.get("nextPageToken")

                if not page_token:
                    break

            logger.info(f"👥 Found {len(students)} students in course")
            return students

        except HttpError as e:
            logger.error(f"❌ HTTP error getting students: {e}")
            return []
        except Exception as e:
            logger.error(f"❌ Error getting students: {e}")
            return []

    def export_students_to_csv(self, output_file: str = "students.csv") -> bool:
        """
        Export students list to CSV file

        Args:
            course_id: Course ID
            output_file: Output CSV file path

        Returns:
            True if successful, False otherwise
        """

        students = self.get_students()

        if not students:
            logger.warning("⚠️ No students found to export")
            return False
        
        out = write_csv_json_file(output_file, students)
        if not out:
            logger.error(f"❌ Error writing to file: {output_file}")
            return False
        logger.info(f"✅ Students exported to {output_file}")
        return True

class Content(Courses):

    def create_announcement(
        self, 
        text: str, 
        materials: List[Dict] = None
    ) -> Optional[str]:
        """
        Create announcement in course

        Args:
            course_id: Course ID
            text: Announcement text
            materials: List of materials to attach

        Returns:
            Announcement ID or None
        """
        announcement_data = {
            "text": text,
            "state": "PUBLISHED",
            "assigneeMode": "ALL_STUDENTS",
        }

        if materials:
            announcement_data["materials"] = materials

        try:
            response = (
                self.classroom_service.announcements()
                .create(courseId=self.course_id, body=announcement_data)
                .execute()
            )

            announcement_id = response.get("id")
            logger.info(f"✅ Announcement created with ID: {announcement_id}")
            return announcement_id

        except HttpError as e:
            logger.error(f"❌ HTTP error creating announcement: {e}")
            return None
        except Exception as e:
            logger.error(f"❌ Error creating announcement: {e}")
            return None
    
    def get_topics(self) -> List[Dict]:
        """
        Get list of topics in course

        Args:
            course_id: Course ID

        Returns:
            List of topics
        """
        try:
            response = (
                self.classroom_service.topics()
                .list(courseId=self.course_id)
                .execute()
            )
            topics = response.get("topic", [])
            logger.info(f"📚 Found {len(topics)} topics in course")
            return topics

        except HttpError as e:
            logger.error(f"❌ HTTP error getting topics: {e}")
            return []
        except Exception as e:
            logger.error(f"❌ Error getting topics: {e}")
            return []


    def create_topic(self, topic_name: str) -> Optional[str]:
        """
        Create topic in course

        Args:
            course_id: Course ID
            topic_name: Topic name

        Returns:
            Topic ID or None
        """
        topics = self.get_topics()
  
        for topic in topics:
            if topic.get("name", "").lower() == topic_name.lower():
                logger.info(
                    f"✅ Topic already exists: {topic_name} (ID: {topic['topicId']})"
                )
                return topic["topicId"]
        try:
            # Create new topic
            topic_data = {"name": topic_name}
            response = (
                self.classroom_service.topics()
                .create(courseId=self.course_id, body=topic_data)
                .execute()
            )

            topic_id = response.get("topicId")
            logger.info(f"✅ Topic created: {topic_name} (ID: {topic_id})")
            return topic_id

        except HttpError as e:
            logger.error(f"❌ HTTP error creating topic: {e}")
            return None
        except Exception as e:
            logger.error(f"❌ Error creating topic: {e}")
            return None

    def create_material(
        self,
        title: str,
        description: str = "",
        topic_id: str = None,
        materials: List[Dict] = None,
        state: str = "PUBLISHED",
    ) -> Optional[str]:
        """
        Create course material

        Args:
            course_id: Course ID
            title: Material title
            description: Material description
            topic_id: Topic ID (optional)
            materials: List of materials to attach
            state: Material state (PUBLISHED or DRAFT)

        Returns:
            Material ID or None
        """
        
        material_data = {"title": title, "description": description, "state": state}
        if topic_id:
            material_data["topicId"] = topic_id
        material_data["materials"] = materials

        try:
            response = (
                self.classroom_service.courseWorkMaterials()
                .create(courseId=self.course_id, body=material_data)
                .execute()
            )

            material_id = response.get("id")
            logger.info(f"✅ Material created: {title} (ID: {material_id})")
            return material_id

        except HttpError as e:
            logger.error(f"❌ HTTP error creating material: {e}")
            return None
        except Exception as e:
            logger.error(f"❌ Error creating material: {e}")
            return None


@dataclass
class ClassroomCourseTemplate:
    """Dataclass representing a Google Classroom course template"""
    name: str
    section: str
    room: str
    description_heading: str
    description: str

    def to_dict(self) -> Dict:
        """Convert template to dictionary for API calls"""
        return asdict(self)
