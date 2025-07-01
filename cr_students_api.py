from typing import List, Dict

from googleapiclient.errors import HttpError
from classroom_api import GoogleClassroomBuild
from fileprocessor import read_csv_json_file, write_csv_json_file
from logger import logger

class Students(GoogleClassroomBuild):

    def __init__(self, course_id):
        super().__init__()
        self.course_id = course_id

    def add_student(self, student_email: str) -> bool:
        """
        Add student to course
        WARNING: You must have domain administrator rights to add students
        DOCS: https://developers.google.com/classroom/reference/rest/v1/courses.students/create

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
                return False
            logger.error(f"❌ Error adding student: {e}")
            raise e

    def add_students_from_file(self, file_path: str, invite: bool = True) -> Dict[str, int]:
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
            if invite:
                try:
                    result = self.invite_student(email)
                    if result:
                       stats["added"] += 1
                    else:
                        stats["already_exists"] += 1
                except Exception as e:
                    logger.error(f"❌ Error inviting student: {e}")
                    stats["failed"] += 1
                continue
            else:
                try:
                    result = self.add_student(email)
                    if result:
                       stats["added"] += 1
                    else:
                        stats["already_exists"] += 1
                except Exception as e:
                    logger.error(f"❌ Error adding student: {e}")
                    stats["failed"] += 1
                continue

        logger.info(
            f"📊 Results: {stats['added']} added, {stats['already_exists']} already exist, {stats['failed']} failed"
        )
        return stats
    
    def invite_student(self, student_email: str) -> bool:
        """
        Send invitation to student (not direct addition)
        """
        try:
            invitation_data = {
                "userId": student_email,
                "courseId": str(self.course_id),
                "role": "STUDENT"
            }
            
            response = (
                self.classroom.invitations()
                .create(body=invitation_data)
                .execute()
            )
            
            logger.info(f"✅ Invitation sent to: {student_email}")
            return True
            
        except HttpError as e:
            if e.resp.status == 409:
                logger.warning(f"⚠️ Invitation already sent to {student_email}")
                return False
            else:
                logger.error(f"❌ HTTP error sending invitation: {e}")
                raise e
    

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