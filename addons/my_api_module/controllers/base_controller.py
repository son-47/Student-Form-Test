import re
from odoo.http import request
import json
from ..helper.normalizer import Normalizer
from ..helper.response_format import responseFormat
from ..helper.serializer import Serializer
import logging
_logger = logging.getLogger(__name__)

class BaseController():
    def __init__(self, modelName, validator):
        self.modelName = modelName
        self.model = request.env[modelName].sudo()
        self.validator = validator

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
            errors = self.validator.validate_create_data(data)
            if errors:
                return responseFormat(code="E603", message="Lỗi kiểm tra dữ liệu : " + " ".join(errors))
            if 'hobbies' in data:
                data['hobbies'] = BaseController.encode_hobbies_binary_string_to_bitmask(data['hobbies'])
                    
            result = self.model.create(data)
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

            data = kw

            errors = self.validator.validate_update_data(kw, id)

            if errors:
                return responseFormat(code="F603", message="Lỗi kiểm tra dữ liệu : " + " ".join(errors))
            
            if 'hobbies' in data:
                data['hobbies'] = BaseController.encode_hobbies_binary_string_to_bitmask(data['hobbies'])
                
            result = self.model.browse(id)

            if not result.exists():
                return responseFormat("F603", message="Lỗi kiểm tra dữ liệu : Ban ghi khong ton tai")

            result.write(data)

            return responseFormat(code=200, data=result.ids )
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

            is_deleted = False

            try:
                data.unlink()
                is_deleted = True
            except:
                is_deleted = False
            
            if is_deleted == False:
                return responseFormat("G605", message="Ban ghi co lien ket khoa ngoai")

            return responseFormat(code=200, data={'id': id})
        except Exception as e:
            return responseFormat(code="G600", message=str(e))
        
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
            for item in data:
                item.unlink()

            return responseFormat(200, data=idlist)
        except Exception as e:
            return responseFormat("I600", message=str(e))