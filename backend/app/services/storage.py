import os
import uuid
from abc import ABC, abstractmethod
from typing import Tuple
from app.core.config import settings

class StorageService(ABC):
    @abstractmethod
    async def save_file(self, user_id: str, original_filename: str, content: bytes) -> Tuple[str, str]:
        """
        Saves a file securely under the user's isolated directory.
        Returns: (stored_filename, relative_file_path)
        """
        pass

    @abstractmethod
    async def get_file_bytes(self, user_id: str, stored_filename: str) -> bytes:
        """
        Retrieves file bytes ensuring user isolation.
        """
        pass

    @abstractmethod
    async def delete_file(self, user_id: str, stored_filename: str) -> bool:
        """
        Deletes a user file.
        """
        pass

class LocalStorageService(StorageService):
    def __init__(self, base_dir: str = settings.STORAGE_LOCAL_PATH):
        self.base_dir = base_dir
        os.makedirs(self.base_dir, exist_ok=True)

    def _get_user_dir(self, user_id: str) -> str:
        # Enforces user-isolated directories: uploads/{user_id}/
        user_dir = os.path.join(self.base_dir, user_id)
        os.makedirs(user_dir, exist_ok=True)
        return user_dir

    async def save_file(self, user_id: str, original_filename: str, content: bytes) -> Tuple[str, str]:
        user_dir = self._get_user_dir(user_id)
        ext = os.path.splitext(original_filename)[1]
        stored_filename = f"{uuid.uuid4()}{ext}"
        file_path = os.path.join(user_dir, stored_filename)

        with open(file_path, "wb") as f:
            f.write(content)

        relative_path = os.path.join(user_id, stored_filename).replace("\\", "/")
        return stored_filename, relative_path

    async def get_file_bytes(self, user_id: str, stored_filename: str) -> bytes:
        user_dir = self._get_user_dir(user_id)
        file_path = os.path.join(user_dir, stored_filename)
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File {stored_filename} not found for user {user_id}")
        
        with open(file_path, "rb") as f:
            return f.read()

    async def delete_file(self, user_id: str, stored_filename: str) -> bool:
        user_dir = self._get_user_dir(user_id)
        file_path = os.path.join(user_dir, stored_filename)
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
        return False

def get_storage_service() -> StorageService:
    # Factory supporting local filesystem for dev and pluggable object storage for prod
    if settings.STORAGE_PROVIDER == "local":
        return LocalStorageService()
    # Future providers: S3StorageService(), GCSStorageService()
    return LocalStorageService()

storage_service = get_storage_service()
