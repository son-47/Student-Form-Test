import os
import logging
from abc import ABC, abstractmethod
from minio import Minio
from werkzeug.utils import secure_filename
from datetime import datetime

_logger = logging.getLogger(__name__)

class FileUploader(ABC):
    """Base class cho các strategy upload file"""
    
    @abstractmethod
    def upload(self, file, entity_type, entity_id):
        """
        Upload file và trả về (attachment_url, attachment)
        
        Returns:
            tuple: (attachment_url, attachment)
            - attachment_url: URL đầy đủ để truy cập file
            - attachment: đường dẫn tương đối (local) hoặc object name (MinIO)
        """
        pass
    def _get_file_subfolder(self, filename):
        ext = filename.lower().split('.')[-1] if '.' in filename else ''
        
        # Phân loại file
        image_extensions = ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp', 'svg']
        document_extensions = ['csv', 'xlsx', 'xls', 'pdf', 'doc', 'docx', 'txt']
        
        if ext in image_extensions:
            return 'images'
        else:
            return 'docs'
        
class LocalFileUploader(FileUploader):
    """Upload file lên filesystem local"""
    
    def __init__(self, base_dir, base_url):
        self.base_dir = base_dir
        self.base_url = base_url
        
    def upload(self, file, entity_type, entity_id):
        if not file or not hasattr(file, 'filename') or not file.filename:
            return "", ""
        #Phân loại file
        sub_folder = self._get_file_subfolder(file.filename)   
        # Tạo tên file unique
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f"{entity_type}_{timestamp}_{entity_id}_{secure_filename(file.filename)}"
        
        # Đường dẫn đầy đủ trong filesystem
        filepath = os.path.join(self.base_dir, sub_folder, filename)

        # Ghi file
        with open(filepath, 'wb') as f:
            file.save(f)
        
        # Trả về (attachment_url, attachment)
        attachment_url = f"{self.base_url}/{sub_folder}/{filename}"
        attachment = f"{sub_folder}/{filename}"  # Đường dẫn tương đối

        _logger.info(f"[LOCAL] File uploaded - URL: {attachment_url}, Path: {attachment}")
        return attachment_url, attachment

class MinioFileUploader(FileUploader):
    """Upload file lên MinIO cloud storage"""
    
    def __init__(self, endpoint, access_key, secret_key, bucket, secure=False):
        self.client = Minio(endpoint, access_key=access_key, secret_key=secret_key, secure=secure)
        self.bucket = bucket
        self.endpoint = endpoint
        self.secure = secure
        
        # Tạo bucket nếu chưa có
        if not self.client.bucket_exists(bucket):
            self.client.make_bucket(bucket)
            
    def upload(self, file, entity_type, entity_id):
        if not file or not hasattr(file, 'filename') or not file.filename:
            return "", ""

        # Phân loại file
        sub_folder = self._get_file_subfolder(file.filename)
        # Tạo object name unique
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f"{entity_type}_{timestamp}_{entity_id}_{secure_filename(file.filename)}"
        object_name = f"{sub_folder}/{filename}"  # VD: Image/student_20241212_123_photo.jpg

        # Upload file
        file.seek(0, os.SEEK_END)
        length = file.tell()
        file.seek(0)
        
        self.client.put_object(
            self.bucket, 
            object_name, 
            file, 
            length,
            content_type=file.content_type or 'application/octet-stream'
        )
        
        # Trả về (attachment_url, attachment)
        attachment_url = f"http://{self.endpoint}/{self.bucket}/{object_name}"
        attachment = object_name  # Object name trong MinIO
        
        _logger.info(f"[MINIO] File uploaded - URL: {attachment_url}, Object: {attachment}")
        return attachment_url, attachment