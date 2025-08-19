import re, os, glob
from odoo.http import request,Response, content_disposition
import json
from ..helper.filehelper import export_file, import_file
from ..helper.normalizer import Normalizer
from ..helper.response_format import responseFormat
from ..helper.serializer import Serializer
from ..helper.file_uploader import LocalFileUploader, MinioFileUploader
from ..helper.upload_config import get_upload_config
from ..helper.file_processor import ImageFileProcessor
from datetime import datetime
from minio import Minio
import logging
import pandas as pd
from datetime import datetime
            
_logger = logging.getLogger(__name__)

class BaseController():
    def __init__(self, modelName, validator):
        self.modelName = modelName
        self.model = request.env[modelName].sudo()
        self.validator = validator
        
        self._init_file_uploader()
        self._init_file_processors()
        # self._init_file_uploader()
    def _init_file_processors(self):
        """Khởi tạo file processors"""
        entity_type = self._get_entity_type()
        
        self.image_processor = ImageFileProcessor(self.file_uploader, entity_type)
        # self.data_processor = DataFileProcessor(self.file_uploader, entity_type, self.validator)
    def _init_file_uploader(self):
        """Khởi tạo file uploader  dựa trên config"""
        upload_type, config = get_upload_config()
        
        if upload_type == "local":
            self.file_uploader = LocalFileUploader(
                config['base_dir'], 
                config['base_url']
            )
        elif upload_type == "minio":
            self.file_uploader = MinioFileUploader(
                config['endpoint'],
                config['access_key'],
                config['secret_key'], 
                config['bucket'],
                config['secure']
            )
        else:
            raise ValueError(f"Unsupported upload type: {upload_type}")

    def _get_entity_type(self):
        """Lấy entity type từ model name"""
        return self.modelName.split('.')[-1]  # 'student' hoặc 'classes'

    
    @staticmethod
    def encode_hobbies_binary_string_to_bitmask(hobbies_input):
            """
            Convert hobbies input to a bitmask (integer).
            - If input is a binary string (e.g., '0,1,1,0,...'), validate and convert to bitmask.
            - If input is a comma-separated list of hobbies (e.g., 'Badminton,Basketball'), convert to binary string then to bitmask.
            """
     
            bits = list(map(int, hobbies_input.strip().split(',')))
            bitmask = 0 
            for i, value in enumerate(bits):
                if value == 1:
                    bitmask |= (1 << i) # giữ nguyên hoặc bằng 2^i
            return bitmask
        
    def get_all(self, kw):
        try:
            columnlist = kw.get("columnlist", "")
            errorMessage, columnlist = Normalizer.getColumnFromAlias(columnlist, self.modelAlias2Fields)
            if errorMessage:
                return responseFormat(code="B600", message=errorMessage)
            data = list(self.model.search([]))
            _logger.info("BAT DAU CHẠY ")
            data = Serializer.serialize(data, columnlist, self.modelFields2Labels)

            return responseFormat(code=200, data=data)
        
        except Exception as e:
            return responseFormat(code="B600", message=str(e))
        
    def get_by_page(self,page, kw):
        try:
            _logger.info("BẮT ĐẦU CHẠY HÀM")
            page = int(page)
            size = int(kw.get('size', 10))

            if (page < 1):
                return responseFormat(code="C601", message="Loi dinh dang so trang")

            if (size < 1):
                return responseFormat(code="C602", message="Loi dinh dang co trang")
            
            order = kw.get('order', None)
            _logger.warning(f"DEBUG - order string input: {order}")
            errMessage, order = Normalizer.getOrderString(order, self.modelAlias2Fields)
            _logger.info("BẮT ĐẦU order ")
            if errMessage:
                return responseFormat(code="C607", message=errMessage)

            domain = []

            search = kw.get('search', None)

            if search:
                domain = ['|', ('name', 'ilike', search), 
               '|', ('description', 'ilike', search), ('code', 'ilike', search)] 

            columnlist = kw.get('columnlist', None)
            _logger.info("DEBUG - BẮT ĐẦU VÀO NORMALIZE")
            errMessage, columnlist = Normalizer.getColumnFromAlias(columnlist, self.modelAlias2Fields)
            _logger.info(f"DEBUG - getColumnFromAlias result: errMessage={errMessage}, columnlist={columnlist}")

            if errMessage:
                return responseFormat(code="C607", message=errMessage)

            offset = (page - 1) * size
            limit = size

            top_records = []

            toplist = kw.get('toplist', None)

            if toplist:
                top_records = list(self.model.search([('id', 'in', toplist.split(','))]))

            total_records = list(self.model.search(
                domain, order=order, limit=limit, offset=offset))
            

            count_records = self.model.search_count(domain)

            data = Serializer.serialize(top_records + total_records, columnlist, self.modelFields2Labels)

            result =  {
                'records': data,
                'pageinfo': {
                    'count': count_records,
                    'current': page,
                    'total_pages': (count_records + int(size) - 1) // int(size),
                    'size': size
                }
            }

            return responseFormat(code = 200, data = result)
        except Exception as e:
            return responseFormat("C600", str(e))
        
    def store(self, kw):
        
        """         
            Phương thức này để thêm mới một bản ghi mới vào database
            Tham số:
                - data: dictionary chứa dữ liệu
            Kiểu trả về:
                - id của bản ghi mới
            Ngoại lệ:
                - E603: Lỗi kiểm tra dữ liệu, nếu dữ liệu không hợp lệ
                - E600: Lỗi không xác định
        """   
  
        try:
            data = kw
            _logger.info(f"Kiểu dữ liệu của dob: {type(kw.get("dob"))}")
            file_data = data.copy()
            file_data.pop('fattachment', None)
            errors = self.validator.validate_create_data(file_data)
            if self._get_entity_type() == 'student':
                self.validator.validate_image_file('fattachment')
            if self.validator.has_errors():
                return responseFormat(
                    code="E603", 
                    message="Lỗi kiểm tra dữ liệu.",
                    data = errors,
                    oldData= file_data,
                )
            if 'hobbies' in data:
                _logger.info(type(data['hobbies']))
                file_data['hobbies'] = BaseController.encode_hobbies_binary_string_to_bitmask(data['hobbies'])
                    
            result = self.model.create(file_data)
            _logger.info(f"Created record with ID: {result.id}")
            #Xử lý file ảnh với ImageProcessor
            file_info = self.image_processor.process('fattachment', result.id)
            if file_info:
                result.write(file_info)
                _logger.info(f"Image info saved: {file_info}")
            
            return responseFormat(code=200, data=result.ids)
        except Exception as e:
            return responseFormat(code="E600", message=str(e))
          
    def get_by_id(self, id, kw):
        """
            Phương thức này trả về thông tin theo id
            Tham số:
                - id: id của record cần lấy thông tin
                - columnlist: danh sách các cột cần lấy dữ liệu, nếu không có sẽ lấy tất cả
            Kiểu trả về:
                - dictionary chứa thông tin 
            Ngoại lệ:
                - D604: Lỗi không tìm thấy bản ghi, nếu không tìm thấy nhà cung cấp
                - D607: Lỗi định dạng cột, nếu columnlist không hợp lệ
        """
        try:
            columnlist = kw.get('columnlist', None)

            errMessage, columnlist = Normalizer.getColumnFromAlias(columnlist, self.modelAlias2Fields)

            if errMessage:
                return responseFormat(code="D607", message=errMessage)

            data = self.model.browse(id)

            if not data.exists():
                return responseFormat("D604", message="Ban ghi khong ton tai")
            
            data = Serializer.serialize_1_item(data, columnlist, self.modelFields2Labels)
            _logger.info(f"trả về type của data : {type(data)}")
            return responseFormat(code=200, data = data)
        except Exception as e:
            return responseFormat(code="D600", message=str(e))
       
        
    def update(self, id, kw):
        """
            Phương thức này dùng để update dữ liệu trên database theo id
            Tham số:
                - id: id của nhà cung cấp cần cập nhật
                - data: dictionary chứa dữ liệu cần cập nhật
            Kiểu trả về:
                - id 
            Ngoại lệ:
                - F603: Lỗi kiểm tra dữ liệu, nếu dữ liệu không hợp lệ
                - F600: Lỗi không xác định, nếu có lỗi không xác định xảy ra
        """
        try:
            data = kw.copy()
            _logger.info(f"DEBUG UPDATE - Request data: {data}")
            
            # **1. Xử lý file CSV/Excel với DataProcessor**
            # data_from_file = self.data_processor.process('file', id, save_file=True)
            # if data_from_file:
            #     data.update(data_from_file)
            #     _logger.info(f"Updated data with file content: {data_from_file}")
            # _logger.info("Đã PROCESS XONG DATA FILE")
            # Validation
            validation_data = data.copy()
            validation_data.pop('fattachment', None)
            # validation_data.pop('file', None)
            _logger.info("KO LỖI")
            errors = self.validator.validate_update_data(validation_data, id)
            if self._get_entity_type() == 'student':
                self.validator.validate_image_file('fattachment')
            if errors:
                return responseFormat(code="F603", message="Lỗi kiểm tra dữ liệu", data=errors, oldData = validation_data )
            _logger.info("KO LỖI 1")
            if 'hobbies' in validation_data:
                validation_data['hobbies'] = BaseController.encode_hobbies_binary_string_to_bitmask(validation_data['hobbies'])
            _logger.info("KO LỖI 2")    
            result = self.model.browse(id)
            if not result.exists():
                return responseFormat("F603", message="Lỗi kiểm tra dữ liệu : Ban ghi khong ton tai")
            
            if self._get_entity_type() == 'student':
            # **2. Xử lý file ảnh với ImageProcessor**
                has_new_image = hasattr(request, 'httprequest') and request.httprequest.files and request.httprequest.files.get('fattachment')
                current_attachment = data.get('attachment', '').strip()
                _logger.info("BẮT ĐẦU NHẬN UPDATE ẢNH")
                if has_new_image:
                    # Upload ảnh mới
                    self.image_processor.cleanup(id)
                    file_info = self.image_processor.process('fattachment', id)
                    if file_info:
                        validation_data.update(file_info)
                        _logger.info(f"Image uploaded: {file_info}")
                        
                else:
                    if current_attachment:
                        _logger.info("Không có thay đổi gì")
                    else:
                    # Xóa ảnh và clear attachment
                        self.image_processor.cleanup(id)
                        validation_data.update({
                            'attachment_url': '',
                            'attachment': ''
                        })
                        _logger.info("Cleared attachment fields and removed images")

            result.write(validation_data)
            return responseFormat(code=200, data=result.ids)
            
        except Exception as e:
            return responseFormat(code="F600", message=str(e))
      
    def destroy(self, id):
        """
            Phương thức này dùng để xóa một bản ghi theo id
            Tham số:
                - id: id của bản ghi cần xóa
            Kiểu trả về:
                - id của bản ghi đã được xóa
            Ngoại lệ:
                - G604: Lỗi không tìm thấy bản ghi
                - G605: Lỗi vi phạm khóa ngoại, nếu có liên kết khóa ngoại
                - G600: Lỗi không xác định, nếu có lỗi không xác định xảy ra
        """
        try:
            data = self.model.browse(id)
            if not data.exists():
                return responseFormat("G604", message="Không tìm thấy bản ghi")

            # Cleanup tất cả file với cả 2 processors
            self.image_processor.cleanup(id)
            # self.data_processor.cleanup(id)
            
            try:
                data.unlink()
                return responseFormat(code=200, data= id)
            except:
                return responseFormat("G605", message="Ban ghi co lien ket khoa ngoai")

        except Exception as e:
            return responseFormat(code="G600", message=str(e))
        # try:
        #     data = self.model.browse(id)

        #     if not data.exists():
        #         return responseFormat("G604", message="Không tìm thấy bản ghi")

        #      # Cleanup files trước khi xóa record
        #     entity_type = self._get_entity_type()
        #     self._cleanup_old_files(entity_type, id)
        #     _logger.info(f"Cleaned up files for {entity_type} ID {id}")
            
        #     is_deleted = False

        #     try:
        #         data.unlink()
        #         is_deleted = True
        #     except:
        #         is_deleted = False
            
        #     if is_deleted == False:
        #         return responseFormat("G605", message="Ban ghi co lien ket khoa ngoai")

        #     return responseFormat(code=200, data= id)
        # except Exception as e:
        #     return responseFormat(code="G600", message=str(e))
        
    def copy(self, id):
        """
            Phương thức này dùng để sao chép một bản ghi theo id
            Tham số:
                - id: id của bản ghi cần sao chép
            Kiểu trả về:
                - id của bản ghi đã được sao chép
            Ngoại lệ:
                - H603: Lỗi kiểm tra dữ liệu
                - H604: Lỗi id không tồn tại
                - H600: Lỗi không xác định, nếu có lỗi không xác định xảy ra
        """
        try:
            data = self.model.browse(id)

            if not data.exists():
                return responseFormat("H604", message="Ban ghi khong ton tai")

            max_id = self.model.search([], order='id desc', limit=1 or 0)
            new_id = max_id.id + 1
            old_code = data.code

            match = re.match(r"^(.*)\s\(\d+\)$", old_code)
            if match:
                base_code = match.group(1)
            else:
                base_code = old_code

            base_code = f"{base_code} ({new_id})"

            new_data = data.copy(default={'code': base_code})
            

            return responseFormat(code=200, data= new_data.ids)
        except Exception as e:
            return responseFormat(code="H600", message=str(e))
        
    
    def mass_copy(self, kw):
        """
            Phương thức này dùng để sao chép nhiều bản ghi theo id
            Tham số:
                - idlist: danh sách các id của bản ghi cần sao chép, ví dụ: [1, 2, 3]
            Kiểu trả về:
                - danh sách các id của bản ghi đã được sao chép
            Ngoại lệ:
                - H603: Lỗi kiểm tra dữ liệu
                - H604: Lỗi danh sách chứa id không tồn tại
                - H600: Lỗi không xác định, nếu có lỗi không xác định xảy ra
        """
        try:
            idlist = kw.get('idlist', None)
            if not idlist:
                return responseFormat("H603", message="Lỗi kiểm tra dữ liệu")

            idlist = list(map(int, idlist.split(',')))

            data = list(self.model.browse(idlist))
            if len(data) != len(idlist):
                return responseFormat("H604", message="Danh sach chua ban ghi khong ton tai")

            new_ids = []
            for id in idlist:

                data = self.model.browse(id)

                max_id = self.model.search([], order='id desc', limit=1 or 0)
                new_id = max_id.id + 1
                old_code = data.code

                match = re.match(r"^(.*)\s\(\d+\)$", old_code)
                if match:
                    base_code = match.group(1)
                else:
                    base_code = old_code

                base_code = f"{base_code} ({new_id})"

                new_id = data.copy(default={'code': base_code}).ids
                new_ids.append(new_id)

            return responseFormat(200, data=new_ids)
        except Exception as e:
            return responseFormat("H600", message=str(e))
        
    def mass_delete(self, kw):
        """
            Phương thức này dùng để xóa nhiều bản ghi theo id
            Tham số:
                - idlist: danh sách các id của bản ghi cần xóa, ví dụ: [1, 2, 3]
            Kiểu trả về:
                - danh sách các id của bản ghi đã được xóa
            Ngoại lệ:
                - I604: Lỗi các bản ghi không xóa được
                - I600: Lỗi không xác định, nếu có lỗi không xác định xảy ra
        """
        try:
            idlist = kw.get('idlist', None)
            if not idlist:
                return responseFormat("I600", message="Danh sach id khong duoc de trong")

            idlist = list(map(int, idlist.split(',')))

            data = list(self.model.browse(idlist))
            for item in data:
                if not item.exists():
                    return responseFormat("i604", message="Lỗi các bản ghi không xóa được : Danh sach chua id khong ton tai")
                else:
                    self.image_processor.cleanup(item.id)
                    # self.data_processor.cleanup(item.id)
                    item.unlink()

            return responseFormat(200, data=idlist)
        except Exception as e:
            return responseFormat("I600", message=str(e))
    def export_by_id(self, id, kw):
        """
            Phương thức này dùng để xuất dữ liệu của một bản ghi theo id
            Tham số:
                - id: id của bản ghi cần xuất
                - columnlist: danh sách các cột cần lấy dữ liệu, nếu không có sẽ lấy tất cả
            Kiểu trả về:
                - file chứa dữ liệu đã được xuất
            Ngoại lệ:
                - K604: Lỗi không tìm thấy bản ghi, nếu không tìm thấy nhà cung cấp
                - K607: Lỗi định dạng cột, nếu columnlist không hợp lệ
        """
        try:
            columnlist = kw.get("columnlist", None)

            errMessage, columnlist = Normalizer.getColumnFromAlias(columnlist, self.modelAlias2Fields)
            if errMessage:
                return responseFormat("K607", message=errMessage)

            file_type = kw.get("type", 'csv')

            data = self.model.browse(id)
            if not data.exists():
                return responseFormat("K604", message="Ban ghi khong ton tai")

            data = Serializer.serialize(data, columnlist, self.modelFields2Labels)
            _logger.info(f"Data đầu ra : {data}")
            return export_file(data, self.modelName, file_type)
        except Exception as e:
            return responseFormat("K600", message=str(e))

    def mass_export(self, kw):
        """
            Phương thức này dùng để xuất dữ liệu của nhiều bản ghi theo id
            Tham số:
                - idlist: danh sách các id của bản ghi cần xuất, nếu không có sẽ lấy tất cả
                - columnlist: danh sách các cột cần lấy dữ liệu, nếu không có sẽ lấy tất cả
            Kiểu trả về:
                - file chứa dữ liệu đã được xuất
            Ngoại lệ:
                -L607: Lỗi danh sách columnList
                -L601: Lỗi định dạng tệp
                -L602:lỖI danh sách bản ghi không tồn tại
                - L600: Lỗi không xác định, nếu có lỗi không xác định xảy ra
        """
        try:
            _logger.info(f"in ra dữ liệu : {kw}")
            idlist = kw.get("idlist", None)
            if not idlist:
                return responseFormat("L602", "Danh sach ban ghi khong ton tai")

            idlist = list(map(int, idlist.split(',')))

            columnlist = kw.get("columnlist", None)
            errMessage, columnlist = Normalizer.getColumnFromAlias(columnlist, self.modelAlias2Fields)
            if errMessage:
                return responseFormat("L607", message=errMessage)

            data = list(self.model.browse(idlist))

            if len(data) != len(idlist):
                return responseFormat("L602", "Danh sach chua ban ghi khong ton tai")

            data = Serializer.serialize(data, columnlist, self.modelFields2Labels)
            _logger.info(f"Data đầu ra: {data}")
            
            type = kw.get("type", "csv")

            return export_file(data, self.modelName, type)
        except Exception as e:
            return responseFormat("L600", message=str(e))

    def import_data(self, kw):
        """
            Phương thức này dùng để nhập dữ liệu từ file
            Tham số:
                - attachment: tệp đính kèm chứa dữ liệu cần nhập
            Kiểu trả về:
                - danh sách các id của bản ghi đã được nhập
            Ngoại lệ:
                -J601: Lỗi định dạng tệp
                -J604:  lỗi tệp dữ liệu chưa tải lên
                -J605: Lỗi không có dữ liệu được thêm mới
                - J600: Lỗi không xác định, nếu có lỗi không xác định xảy ra
        """
        
        # try:
        #     attachment = kw.get("attachment", None)
            
        #     if not attachment:
        #         return responseFormat(
        #             code="J604", 
        #             message="File không được tải lên",
        #             data=[]
        #         )

        #     # Validate file và lấy dữ liệu hợp lệ
        #     df= self.validator.validate_import_file(attachment)
            
        #     if self.validator.get_errors():
        #         # return responseFormat("J601", "Lỗi validation file: " + " ".join(self.validator.get_errors()))
        #         return responseFormat(
        #         code="J601", 
        #         message="Lỗi định dạng tệp",
        #         data=self.validator.get_errors()  # Chi tiết lỗi validation file
        #     )
        
            
            # if not valid_records:
            #     return responseFormat("J605", "File không chứa dữ liệu hợp lệ")
            
            # Tạo records từ dữ liệu đã validate
        #     created_records = []
        #     for record_data in valid_records:
        #         try:
        #             # Xử lý dữ liệu trước khi tạo
        #             if 'hobbies' in record_data:
        #                 record_data['hobbies'] = BaseController.encode_hobbies_binary_string_to_bitmask(record_data['hobbies'])
                    
        #             # Tạo record
        #             new_record = self.model.create(record_data)
        #             created_records.append(new_record.id)
                    
        #         except Exception as e:
        #             _logger.error(f"Error creating record {record_data}: {str(e)}")
        #             continue

        #     return responseFormat(200, data= created_records)
        # except Exception as e:
            # return responseFormat("J600", str(e))
        try: 
             # Validate import file
            if not self.validator.validate_import_file('attachment', 10):  # 10MB max
                return responseFormat(
                    code="J601", 
                    message="Loi dinh dang tep.",
                    errors=self.validator.get_errors()
                )
                
            attachment = kw.get("attachment", None)

            if not attachment:
                return responseFormat("J604", "Tai tep du lieu khong thanh cong")

            data = import_file(attachment)
            
            if not data:
                return responseFormat("J605", "Khong the doc tep du lieu")
            
            self.model.create(data)
                

            return responseFormat(200, data = data)
        except Exception as e:
            return responseFormat("J600", str(e))