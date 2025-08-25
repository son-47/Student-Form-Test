# addons/my_api_module/helper/file_processor.py
from abc import ABC, abstractmethod
from odoo.http import request, Response, content_disposition
from .file_uploader import LocalFileUploader, MinioFileUploader
import os
import glob
import io
from datetime import datetime
from werkzeug.utils import secure_filename        
import pandas as pd
import logging

_logger = logging.getLogger(__name__)

class FileProcessor(ABC):
    """Base class cho xử lý file"""
    
    def __init__(self, file_uploader, entity_type):
        self.file_uploader = file_uploader
        self.entity_type = entity_type
    
    @abstractmethod
    def process(self, file_key, entity_id, **kwargs):
        """Xử lý file từ request"""
        pass
    
    @abstractmethod
    def cleanup(self, entity_id):
        """Xóa file cũ"""
        pass

class ImageFileProcessor(FileProcessor):
    """Xử lý file ảnh - upload và lưu trữ để hiển thị"""
    
    def process(self, file_key, entity_id, **kwargs):
        """
        Upload ảnh và trả về thông tin để lưu DB
        Returns:
            dict: {'attachment_url': '', 'attachment': ''} hoặc {}
        """
        # if not hasattr(request, 'httprequest') or not request.httprequest.files:
        #     return {}
            
        # file = request.httprequest.files.get(file_key)
        # if not file or not hasattr(file, 'filename') or not file.filename:
        #     return {}
        
        # # Validate file type
        # if not self._is_image_file(file.filename):
        #     _logger.warning(f"File {file.filename} is not an image")
        #     return {}
        
        try:
            file = request.httprequest.files.get(file_key)
            # Upload image
            attachment_url, attachment = self.file_uploader.upload(file, self.entity_type, entity_id)
            
            if attachment_url and attachment:
                _logger.info(f"Image processed - URL: {attachment_url}, Path: {attachment}")
                return {
                    'attachment_url': attachment_url,
                    'attachment': attachment
                }
            return {}
            
        except Exception as e:
            _logger.error(f"Error processing image: {str(e)}")
            return {}
    
    def cleanup(self, entity_id):
        """Xóa chỉ file ảnh cũ"""
        try:
            if isinstance(self.file_uploader, LocalFileUploader):
                pattern = os.path.join(
                    self.file_uploader.base_dir,
                    'images',
                    f"{self.entity_type}_*_{entity_id}_*"
                )
                old_files = glob.glob(pattern)
                for old_file in old_files:
                    try:
                        os.remove(old_file)
                        _logger.info(f"Removed old image: {old_file}")
                    except Exception as e:
                        _logger.warning(f"Failed to remove image {old_file}: {e}")
            
            elif isinstance(self.file_uploader, MinioFileUploader):
                client = self.file_uploader.client
                bucket = self.file_uploader.bucket
                prefix = f"images/{self.entity_type}_"
                suffix = f"_{entity_id}_"
                
                try:
                    objects = client.list_objects(bucket, prefix=prefix, recursive=True)
                    for obj in objects:
                        if suffix in obj.object_name:
                            client.remove_object(bucket, obj.object_name)
                            _logger.info(f"Removed old MinIO image: {obj.object_name}")
                except Exception as e:
                    _logger.warning(f"Failed to remove MinIO images: {e}")
                    
        except Exception as e:
            _logger.error(f"Error cleaning up images: {str(e)}")
    
    # def _is_image_file(self, filename):
    #     """Kiểm tra file có phải ảnh không"""
    #     image_extensions = ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp', 'svg']
    #     ext = filename.lower().split('.')[-1] if '.' in filename else ''
    #     return ext in image_extensions

# class DataFileProcessor(FileProcessor):
#     """Xử lý file CSV/Excel - đọc data và có thể lưu trữ để audit"""
    
#     def __init__(self, file_uploader, entity_type, validator=None):
#         super().__init__(file_uploader, entity_type)
#         self.validator = validator
        
#     def process(self, file_key, entity_id, **kwargs):
#         """
#         Đọc file CSV/Excel và trả về data + có thể lưu file
#         Returns:
#             dict: data từ file hoặc {}
#         """
#         if not hasattr(request, 'httprequest') or not request.httprequest.files:
#             return {}
            
#         files = request.httprequest.files.getlist(file_key)
#         if not files:
#             return {}
            
#         file = files[0]
#         if not file or not file.filename:
#             return {}
        
#         # Validate file type
#         if not self._is_data_file(file.filename):
#             _logger.warning(f"File {file.filename} is not a data file")
#             return {}
        
#         try:
#             # Validate file nếu có validator
#             if self.validator:
#                 clean_data = self.validator.validate_update_file(file)
#                 if self.validator.get_errors():
#                     _logger.warning(f"File validation errors: {self.validator.get_errors()}")
#                     return {}
                
#                 if clean_data:
#                     # Cleanup old files
#                     self.cleanup(entity_id)
                    
#                     # Lưu file để audit
#                     save_file = kwargs.get('save_file', True)
#                     if save_file:
#                         self._save_file_for_audit(file, entity_id)
                    
#                     _logger.info(f"File data validated and extracted: {clean_data}")
#                     return clean_data
#             else:
#                 # Fallback to old logic nếu không có validator
#                 data = self._extract_data_from_file(file)
                
#                 # Cleanup old files
#                 self.cleanup(entity_id)

#                 # Lưu file để audit (optional)
#                 save_file = kwargs.get('save_file', True)
#                 if save_file and data:
#                     self._save_file_for_audit(file, entity_id)
                
#                 return data
            
#         except Exception as e:
#             _logger.error(f"Error processing data file: {str(e)}")
#             return {}
    
#     def cleanup(self, entity_id):
#         """Xóa chỉ file docs cũ"""
#         try:
#             if isinstance(self.file_uploader, LocalFileUploader):
#                 pattern = os.path.join(
#                     self.file_uploader.base_dir,
#                     'docs',
#                     f"{self.entity_type}_*_{entity_id}_*"
#                 )
#                 old_files = glob.glob(pattern)
#                 for old_file in old_files:
#                     try:
#                         os.remove(old_file)
#                         _logger.info(f"Removed old data file: {old_file}")
#                     except Exception as e:
#                         _logger.warning(f"Failed to remove data file {old_file}: {e}")
            
#             elif isinstance(self.file_uploader, MinioFileUploader):
#                 client = self.file_uploader.client
#                 bucket = self.file_uploader.bucket
#                 prefix = f"docs/{self.entity_type}_"
#                 suffix = f"_{entity_id}_"
                
#                 try:
#                     objects = client.list_objects(bucket, prefix=prefix, recursive=True)
#                     for obj in objects:
#                         if suffix in obj.object_name:
#                             client.remove_object(bucket, obj.object_name)
#                             _logger.info(f"Removed old MinIO data file: {obj.object_name}")
#                 except Exception as e:
#                     _logger.warning(f"Failed to remove MinIO data files: {e}")
                    
#         except Exception as e:
#             _logger.error(f"Error cleaning up data files: {str(e)}")
    
#     def _is_data_file(self, filename):
#         """Kiểm tra file có phải data file không"""
#         data_extensions = ['csv', 'xlsx', 'xls']
#         ext = filename.lower().split('.')[-1] if '.' in filename else ''
#         return ext in data_extensions
    
#     def _extract_data_from_file(self, file):
#         """Đọc data từ CSV/Excel file"""
#         try:
#             # Reset file pointer
#             file.seek(0)
            
#             # Đọc file tùy theo extension
#             if file.filename.lower().endswith('.csv'):
#                 content = file.stream.read().decode('utf-8-sig')
#                 df = pd.read_csv(io.StringIO(content))
#             elif file.filename.lower().endswith(('.xls', '.xlsx')):
#                 df = pd.read_excel(file.stream)
#             else:
#                 _logger.warning(f"Unsupported file format: {file.filename}")
#                 return {}
            
#             if df.empty:
#                 return {}
                
#             # Trả về record đầu tiên dưới dạng dict
#             record = df.iloc[0].to_dict()
            
#             # Loại bỏ các giá trị NaN và None
#             clean_record = {}
#             for k, v in record.items():
#                 if pd.notna(v) and v is not None and str(v).strip():
#                     clean_record[k] = str(v).strip()
            
#             _logger.info(f"Extracted data from file: {clean_record}")
#             return clean_record
            
#         except Exception as e:
#             _logger.error(f"Error extracting data from file: {str(e)}")
#             return {}
    
#     def _save_file_for_audit(self, file, entity_id):
#         try:
#             # Reset file pointer
#             file.seek(0)
            
#             timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
#             filename = f"{self.entity_type}_{timestamp}_{entity_id}_{secure_filename(file.filename)}"
            
#             if isinstance(self.file_uploader, LocalFileUploader):
#                 docs_dir = os.path.join(self.file_uploader.base_dir, 'docs')
#                 os.makedirs(docs_dir, exist_ok=True)
                
#                 filepath = os.path.join(docs_dir, filename)
#                 with open(filepath, 'wb') as f:
#                     file.save(f)
                
#                 _logger.info(f"Data file saved for audit: {filepath}")
            
#             elif isinstance(self.file_uploader, MinioFileUploader):
#                 object_name = f"docs/{filename}"
                
#                 file.seek(0, os.SEEK_END)
#                 length = file.tell()
#                 file.seek(0)
                
#                 self.file_uploader.client.put_object(
#                     self.file_uploader.bucket,
#                     object_name,
#                     file,
#                     length,
#                     content_type=file.content_type or 'application/octet-stream'
#                 )
                
#                 _logger.info(f"Data file saved to MinIO for audit: {object_name}")
                
#         except Exception as e:
#             _logger.error(f"Error saving file for audit: {str(e)}")