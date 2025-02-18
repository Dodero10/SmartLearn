from datetime import datetime
from typing import List, Optional, Dict, Any
from .models import User, Project, Chat, Message, File, Setting
from bson import ObjectId

class DatabaseService:
    @staticmethod
    def get_history(user_id: str) -> List[Dict[str, Any]]:
        """Lấy lịch sử chat của user"""
        try:
            projects = Project.objects(user_id=user_id, active=True)
            history = []
            for project in projects:
                chats = Chat.objects(project_id=project.id, active=True)
                project_data = {
                    "project_id": str(project.id),
                    "project_name": project.project_name,
                    "chats": [{
                        "chat_id": str(chat.id),
                        "title": chat.title,
                        "timestamp": chat.timestamp
                    } for chat in chats]
                }
                history.append(project_data)
            return history
        except Exception as e:
            raise Exception(f"Lỗi khi lấy lịch sử chat: {str(e)}")

    @staticmethod
    def get_setting(user_id: str, key: str) -> Optional[str]:
        """Lấy giá trị setting của user"""
        try:
            setting = Setting.objects(user_id=user_id, key=key).first()
            return setting.value if setting else None
        except Exception as e:
            raise Exception(f"Lỗi khi lấy setting: {str(e)}")

    @staticmethod
    def create_project(user_id: str, project_name: str) -> str:
        """Tạo project mới"""
        try:
            project = Project(
                user_id=user_id,
                project_name=project_name
            ).save()
            return str(project.id)
        except Exception as e:
            raise Exception(f"Lỗi khi tạo project: {str(e)}")

    @staticmethod
    def create_chat(project_id: str, title: str) -> str:
        """Tạo chat mới trong project"""
        try:
            chat = Chat(
                project_id=project_id,
                title=title
            ).save()
            return str(chat.id)
        except Exception as e:
            raise Exception(f"Lỗi khi tạo chat: {str(e)}")

    @staticmethod
    def upload_file(chat_id: str, file_name: str, file_type: str, size: int) -> str:
        """Upload file vào chat"""
        try:
            file = File(
                chat_id=chat_id,
                file_name=file_name,
                file_type=file_type,
                size=size
            ).save()
            return str(file.id)
        except Exception as e:
            raise Exception(f"Lỗi khi upload file: {str(e)}")

    @staticmethod
    def send_message(chat_id: str, role: str, content: str) -> str:
        """Gửi tin nhắn trong chat"""
        try:
            message = Message(
                chat_id=chat_id,
                role=role,
                content=content
            ).save()
            return str(message.id)
        except Exception as e:
            raise Exception(f"Lỗi khi gửi tin nhắn: {str(e)}")

    @staticmethod
    def push_setting(user_id: str, key: str, value: str) -> None:
        """Cập nhật hoặc tạo mới setting"""
        try:
            Setting.objects(user_id=user_id, key=key).update_one(
                set__value=value,
                upsert=True
            )
        except Exception as e:
            raise Exception(f"Lỗi khi cập nhật setting: {str(e)}")

    @staticmethod
    def delete_chat(chat_id: str) -> None:
        """Xóa chat (soft delete)"""
        try:
            Chat.objects(id=chat_id).update_one(set__active=False)
        except Exception as e:
            raise Exception(f"Lỗi khi xóa chat: {str(e)}")

    @staticmethod
    def get_chat_messages(chat_id: str) -> List[Dict[str, Any]]:
        """Lấy tất cả tin nhắn trong chat"""
        try:
            messages = Message.objects(chat_id=chat_id).order_by('timestamp')
            return [{
                "message_id": str(msg.id),
                "role": msg.role,
                "content": msg.content,
                "timestamp": msg.timestamp
            } for msg in messages]
        except Exception as e:
            raise Exception(f"Lỗi khi lấy tin nhắn: {str(e)}")

    @staticmethod
    def delete_file_in_chat(file_id: str) -> None:
        """Xóa file khỏi chat"""
        try:
            File.objects(id=file_id).delete()
        except Exception as e:
            raise Exception(f"Lỗi khi xóa file: {str(e)}")

    @staticmethod
    def update_name_project(project_id: str, new_name: str) -> None:
        """Cập nhật tên project"""
        try:
            Project.objects(id=project_id).update_one(set__project_name=new_name)
        except Exception as e:
            raise Exception(f"Lỗi khi đổi tên project: {str(e)}")

    @staticmethod
    def update_name_chat(chat_id: str, new_title: str) -> None:
        """Cập nhật tên chat"""
        try:
            Chat.objects(id=chat_id).update_one(set__title=new_title)
        except Exception as e:
            raise Exception(f"Lỗi khi đổi tên chat: {str(e)}")

    @staticmethod
    def search_chat(user_id: str, keyword: str) -> List[Dict[str, Any]]:
        """Tìm kiếm chat theo từ khóa"""
        try:
            # Tìm tất cả project của user
            projects = Project.objects(user_id=user_id, active=True)
            project_ids = [p.id for p in projects]
            
            # Tìm chat trong các project có title chứa keyword
            chats = Chat.objects(
                project_id__in=project_ids,
                title__icontains=keyword,
                active=True
            )
            
            return [{
                "chat_id": str(chat.id),
                "project_id": str(chat.project_id.id),
                "project_name": chat.project_id.project_name,
                "title": chat.title,
                "timestamp": chat.timestamp
            } for chat in chats]
        except Exception as e:
            raise Exception(f"Lỗi khi tìm kiếm chat: {str(e)}") 