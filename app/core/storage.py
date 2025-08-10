import os
from abc import ABC, abstractmethod
from google.cloud import storage
from app.core.config import settings

class StorageClient(ABC):
    @abstractmethod
    def upload_file(self, source_file_path: str, destination_blob_name: str):
        pass

    @abstractmethod
    def download_file(self, source_blob_name: str, destination_file_path: str):
        pass

    @abstractmethod
    def list_files(self, prefix: str) -> list[str]:
        pass

    @abstractmethod
    def delete_file(self, blob_name: str):
        pass

class GCSStorageClient(StorageClient):
    def __init__(self):
        self.client = storage.Client(project=settings.GCP_PROJECT_ID)
        self.bucket = self.client.bucket(settings.GCS_BUCKET_NAME)

    def upload_file(self, source_file_path: str, destination_blob_name: str):
        blob = self.bucket.blob(destination_blob_name)
        blob.upload_from_filename(source_file_path)
        print(f"File {source_file_path} uploaded to {destination_blob_name}.")

    def download_file(self, source_blob_name: str, destination_file_path: str):
        blob = self.bucket.blob(source_blob_name)
        blob.download_to_filename(destination_file_path)
        print(f"Blob {source_blob_name} downloaded to {destination_file_path}.")

    def list_files(self, prefix: str) -> list[str]:
        blobs = self.client.list_blobs(self.bucket, prefix=prefix)
        return [blob.name for blob in blobs]

    def delete_file(self, blob_name: str):
        blob = self.bucket.blob(blob_name)
        blob.delete()
        print(f"Blob {blob_name} deleted.")

class MockStorageClient(StorageClient):
    def __init__(self):
        self.base_dir = "./local_storage_mock"
        os.makedirs(self.base_dir, exist_ok=True)

    def _get_full_path(self, blob_name: str) -> str:
        return os.path.join(self.base_dir, blob_name)

    def upload_file(self, source_file_path: str, destination_blob_name: str):
        full_path = self._get_full_path(destination_blob_name)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(source_file_path, "rb") as src, open(full_path, "wb") as dest:
            dest.write(src.read())
        print(f"Mock: File {source_file_path} uploaded to {full_path}.")

    def download_file(self, source_blob_name: str, destination_file_path: str):
        full_path = self._get_full_path(source_blob_name)
        os.makedirs(os.path.dirname(destination_file_path), exist_ok=True)
        with open(full_path, "rb") as src, open(destination_file_path, "wb") as dest:
            dest.write(src.read())
        print(f"Mock: Blob {source_blob_name} downloaded to {destination_file_path}.")

    def list_files(self, prefix: str) -> list[str]:
        # This is a simplified mock list_files. In a real scenario, you might
        # want to walk the directory tree and filter by prefix.
        all_files = []
        for root, _, files in os.walk(self.base_dir):
            for file in files:
                relative_path = os.path.relpath(os.path.join(root, file), self.base_dir)
                if relative_path.startswith(prefix):
                    all_files.append(relative_path)
        return all_files

    def delete_file(self, blob_name: str):
        full_path = self._get_full_path(blob_name)
        if os.path.exists(full_path):
            os.remove(full_path)
            print(f"Mock: File {full_path} deleted.")
        else:
            print(f"Mock: File {full_path} not found.")

def get_storage_client() -> StorageClient:
    if settings.ENV == "production":
        return GCSStorageClient()
    else:
        return MockStorageClient()

storage_client = get_storage_client()
