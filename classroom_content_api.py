from googleapiclient.errors import HttpError
from classroom_api import GoogleClassroomBuild
from typing import List, Dict, Optional
from logger import logger

class Content(GoogleClassroomBuild):

    def __init__(self, course_id):
        super().__init__()
        self.course_id = course_id


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
