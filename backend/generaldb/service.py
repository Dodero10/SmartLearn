from datetime import datetime
from typing import List, Optional, Dict, Any
from .models import User, Chat, Message, File, Setting
from bson import ObjectId

class DatabaseService:
    @staticmethod
    def get_history(user_id: str) -> List[Dict[str, Any]]:
        """Lấy lịch sử chat của user"""
        try:
            chats = Chat.objects(user_id=user_id, active=True)
            return [{
                "chat_id": str(chat.id),
                "title": chat.title,
                "timestamp": chat.timestamp
            } for chat in chats]
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
    def create_chat(user_id: str, title: str) -> str:
        """Tạo chat mới cho user"""
        try:
            chat = Chat(
                user_id=user_id,
                title=title
            ).save()
            return str(chat.id)
        except Exception as e:
            raise Exception(f"Lỗi khi tạo chat: {str(e)}")

    @staticmethod
    def upload_file(user_id: str, file_name: str, file_type: str) -> str:
        """Upload file cho user"""
        try:
            file = File(
                user_id=user_id,
                file_name=file_name,
                file_type=file_type
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
    def get_user_files(user_id: str) -> List[Dict[str, Any]]:
        """Lấy danh sách file của user"""
        try:
            files = File.objects(user_id=user_id)
            return [{
                "file_id": str(file.id),
                "file_name": file.file_name,
                "file_type": file.file_type,
                "upload_date": file.upload_date,
                "selected": file.selected
            } for file in files]
        except Exception as e:
            raise Exception(f"Lỗi khi lấy danh sách file: {str(e)}")

    @staticmethod
    def delete_file(file_id: str) -> None:
        """Xóa file của user"""
        try:
            File.objects(id=file_id).delete()
        except Exception as e:
            raise Exception(f"Lỗi khi xóa file: {str(e)}")

    @staticmethod
    def toggle_file_selection(file_id: str) -> None:
        """Toggle trạng thái selected của file"""
        try:
            file = File.objects(id=file_id).first()
            if file:
                file.selected = not file.selected
                file.save()
        except Exception as e:
            raise Exception(f"Lỗi khi thay đổi trạng thái file: {str(e)}")

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
            chats = Chat.objects(
                user_id=user_id,
                title__icontains=keyword,
                active=True
            )
            
            return [{
                "chat_id": str(chat.id),
                "title": chat.title,
                "timestamp": chat.timestamp
            } for chat in chats]
        except Exception as e:
            raise Exception(f"Lỗi khi tìm kiếm chat: {str(e)}") 