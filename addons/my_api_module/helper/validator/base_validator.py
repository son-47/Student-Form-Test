import re
import pandas as pd
import io
from abc import ABC, abstractmethod
from odoo.http import request, Response
class BaseValidator(ABC):
    def __init__(self, data=None, model=None, modelFields2Labels=None):
        self.data = data or {}  
        self.errors = {}
        self.model = model
        self.modelFields2Labels = modelFields2Labels

        self.rules = {}
        self.message_templates = self.get_default_message_templates()
        self.define_rules()

    @abstractmethod
    def define_rules(self):
        """định nghĩa rules"""
        pass

    def define_field_rules(self, rules):
        """Định nghĩa rules cho từng field"""
        self.rules = rules
        
    def get_default_message_templates(self):
        """Định nghĩa message"""
        return {
            'required': '{} không được để trống.',
            'unique': '{} đã tồn tại.',
            'max_length': '{} tối đa {} ký tự.',
            'min_length': '{} tối thiểu {} ký tự.',
            'email': '{} không đúng định dạng email.',
            'facebook': '{} không đúng định dạng Facebook.',
            'date': '{} không đúng định dạng ngày sinh.',
            'list': '{} không đúng định dạng sở thích.',
            'number': '{} phải là số.',
        }
        
    def get_field_label(self, field_name):
        """
        Lấy label hiển thị của field từ enum modelFields2Labels
        """
        if self.modelFields2Labels:
            try:
                # Tìm enum member có name = field_name
                for field_enum in self.modelFields2Labels:
                    if field_enum.name == field_name:
                        return field_enum.value
            except:
                pass
         
        return field_name

    def get_errors(self):
        return self.errors
    
    # def clear_errors(self):
    #     self.errors = {}
        
    def add_error(self, field, message):
        if field not in self.errors:
            self.errors[field] = []
        self.errors[field].append(message)
    
    def has_errors(self):
        return len(self.errors) > 0
    
    def validate_create_data(self, data):
        """Validate cho CREATE - tất cả fields có rules"""
        self.data = data
        self.errors = {}
        
        for field_name, field_rules in self.rules.items():
            self._validate_field(field_name, field_rules, context='create')
            
        return self.get_errors()

    def validate_update_data(self, data, entity_id):
        """Validate cho UPDATE - chỉ fields có trong data"""
        self.data = data
        self.errors = {}
        
        # Chỉ validate fields có trong data
        for field_name in data.keys():
            if field_name in self.rules:
                self._validate_field(field_name, self.rules[field_name], context='update', entity_id=entity_id)
                
        return self.get_errors()
    
    def validate_create_data(self, data):
        """Validate cho CREATE - tất cả fields có rules"""
        self.data = data
        self.errors = {}
        
        for field_name, field_rules in self.rules.items():
            self._validate_field(field_name, field_rules, context='create')
            
        return self.get_errors()

    def validate_update_data(self, data, entity_id):
        """Validate cho UPDATE - chỉ fields có trong data"""
        self.data = data
        self.errors = {}
        
        # Chỉ validate fields có trong data
        for field_name in data.keys():
            if field_name in self.rules:
                self._validate_field(field_name, self.rules[field_name], context='update', entity_id=entity_id)
                
        return self.get_errors()
    
    def _validate_field(self, field_name, field_rules, context='create', entity_id=None):
        """Validate một field theo rules"""
        field_label = self.get_field_label(field_name)
        
        for rule_type, rule_config in field_rules.items():
            if not rule_config:  # Skip nếu rule = False hoặc None
                continue
                
            # Skip required validation cho update context
            if rule_type == 'required' and context == 'update':
                continue
                
            self.apply_rule(field_name, field_label, rule_type, rule_config, entity_id)

    def apply_rule(self, field_name, field_label, rule_type, rule_config, entity_id=None):
        """Apply một rule cụ thể"""
        if rule_type == 'required' and rule_config:
            self.check_required(field_name, field_label)
            
        elif rule_type == 'unique' and rule_config:
            self.check_unique(field_name, field_label, entity_id)
            
        elif rule_type == 'max_length' and rule_config:
            self.check_max_length(field_name, field_label, rule_config)
            
        elif rule_type == 'min_length' and rule_config:
            self.check_min_length(field_name, field_label, rule_config)
            
        elif rule_type == 'email' and rule_config:
            self.check_email(field_name, field_label)
            
        elif rule_type == 'facebook' and rule_config:
            self.check_facebook(field_name, field_label)
            
        elif rule_type == 'date' and rule_config:
            self.check_date(field_name, field_label)
            
        elif rule_type == 'list' and rule_config:
            self.check_list(field_name, field_label)
        
        elif rule_type == 'number' and rule_config:
            self.check_number(field_name, field_label)

    # Validation methods
    def check_required(self, field, field_label):
        value = self.data.get(field)
        if value is None or str(value).strip() == "":
            message = self.message_templates['required'].format(field_label)
            self.add_error(field, message)

    def check_unique(self, field, field_label, except_id=None):
        value = self.data.get(field)
        if value is None or not str(value).strip():
            return 
            
        value = str(value).strip()
        domain = [(field, '=', value)]
        if except_id:
            domain.append(('id', '!=', except_id))
        if self.model.search(domain, limit=1):
            message = self.message_templates['unique'].format(field_label)
            self.add_error(field, message)

    def check_max_length(self, field, field_label, max_length):
        value = self.data.get(field)
        if value is None:
            return
            
        value_str = str(value).strip()
        if len(value_str) > max_length:
            message = self.message_templates['max_length'].format(field_label, max_length)
            self.add_error(field, message)

    def check_min_length(self, field, field_label, min_length):
        value = self.data.get(field)
        if value is None:
            return
        value_str =str(value).strip()
        if len(value_str) < min_length:
            message = self.message_templates['min_length'].format(field_label, min_length)
            self.add_error(field, message)

    # def check_range_length(self, field, field_label, min_length, max_length):
    #     value = self.data.get(field)
    #     if value is None:
    #         return
    #     value_str = str(value).strip()
    #     if not (min_length <= len(value_str) <= max_length):
    #         self.add_error(field, f"{field} phải có độ dài từ {min_length} đến {max_length} ký tự.")

    def check_min(self, field, field_label, min_value):
        value = self.data.get(field)
        if value is None:
            return
        value = float(value)
        if value < min_value:
            message = self.message_templates['min'].format(field_label, min_value)
            self.add_error(field, message)

    def check_max(self, field, field_label, max_value):
        value = self.data.get(field)
        if value is None:
            return
        value = float(value)
        if value > max_value:
            message = self.message_templates['max'].format(field_label, max_value)
            self.add_error(field, message)

    # def check_range(self, field, min_value, max_value):
    #     value = self.data.get(field)
    #     if value is None:
    #         return
    #     value = float(value)
    #     if not (min_value <= value <= max_value):
    #         self.add_error(field, f"{field} phải nằm trong khoảng [{min_value}, {max_value}].")
    
    def check_number(self, field):
        value = self.data.get(field)
        if value is None:
            return
        if not isinstance(value, float):
            message = self.message_templates['number'].format(field_label)
            self.add_error(field, message)
        
            
    def check_email(self, field, field_label):
        value = self.data.get(field, '')
        if not value:
            return
            
        regex_email = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,7}\b'
        if not re.match(regex_email, value):
            message = self.message_templates['email'].format(field_label)
            self.add_error(field, message)
    
    def check_facebook(self, field, field_label):
        value = self.data.get(field, '')
        if not value:
            return
            
        regex_facebook = r'^(https?:\/\/)?(www\.)?facebook\.com\/[A-Za-z0-9\.]+\/?$'
        if not re.match(regex_facebook, value):
            message = self.message_templates['facebook'].format(field_label)
            self.add_error(field, message)

    def check_date(self, field, field_label):
        value = self.data.get(field, '')
        if not value:
            return
            
        regex_date = r'^\d{4}\-(0?[1-9]|1[012])\-(0?[1-9]|[12][0-9]|3[01])$'
        if not re.match(regex_date, value):
            message = self.message_templates['date'].format(field_label)
            self.add_error(field, message)

    def check_list(self, field, field_label):
        value = self.data.get(field)
        if not value :
            return
                
        if not isinstance(value, str) or len(value) != 57:
            message = self.message_templates['list'].format(field_label)
            self.add_error(field, message)
        else:
            regex_list = r'^(0|1)(,(0|1)){28}$'
            if not re.match(regex_list, value):
                message = self.message_templates['list'].format(field_label)
                self.add_error(field, message)

  
    
    # def prepare_update_rules(self, entity_id):
    #     """Chuẩn bị update rules với id được gọi cho unique validation"""
    #     for field_name, field_rules in self.update_rules.items():
    #         for i, rule in enumerate(field_rules):
    #             if rule == 'unique_value':
    #                 self.update_rules[field_name][i] = f'unique_value:{entity_id}'
                       
                    

    def validate_image_file(self, file_key='fattachment', max_size_mb=5):
        """Validate file ảnh trong request"""
        if not hasattr(request, 'httprequest') or not request.httprequest.files:
            return True  # Không bắt buộc
            
        file = request.httprequest.files.get(file_key)
        if not file or not file.filename:
            return True  # Không bắt buộc
            
        # Check format
        image_exts = ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp', 'svg']
        ext = file.filename.lower().split('.')[-1] if '.' in file.filename else ''
        if ext not in image_exts:
            self.add_error(file_key, "Chỉ hỗ trợ file ảnh.")
            return False
            
        # Check size, đưa con trỏ về cuối file
        file.seek(0, 2)
        size = file.tell()
        file.seek(0)
        if size > max_size_mb * 1024 * 1024:
            self.add_error(file_key, f"File ảnh quá lớn. Kích thước tối đa: {max_size_mb}MB.")
            return False
            
        return True

    def validate_import_file(self, file_key='attachment', max_size_mb=10):
        """Validate file import trong request"""
        if not hasattr(request, 'httprequest') or not request.httprequest.files:
            self.add_error(file_key, "File không được tải lên.")
            return False
            
        file = request.httprequest.files.get(file_key)
        if not file or not file.filename:
            self.add_error(file_key, "File không được tải lên.")
            return False
            
        # Check format
        data_exts = ['csv', 'xlsx', 'xls']
        ext = file.filename.lower().split('.')[-1] if '.' in file.filename else ''
        if ext not in data_exts:
            self.add_error(file_key, "Chỉ hỗ trợ file CSV hoặc Excel.")
            return False
            
        # Check size
        file.seek(0, 2)
        size = file.tell()
        file.seek(0)
        if size > max_size_mb * 1024 * 1024:
            self.add_error(file_key, f"File quá lớn. Kích thước tối đa: {max_size_mb}MB.")
            return False
            
        return True
    
    # def validate_file_format(self, file):
    #     """Validate định dạng file"""
    #     if not file or not hasattr(file, 'filename') or not file.filename:
    #         self.add_error("File không hợp lệ hoặc không có tên.")
    #         return False
            
    #     filename = file.filename.lower()
    #     allowed_extensions = ['.csv', '.xlsx', '.xls']
        
    #     if not any(filename.endswith(ext) for ext in allowed_extensions):
    #         self.add_error("Chỉ hỗ trợ file CSV (.csv) hoặc Excel (.xlsx, .xls).")
    #         return False
            
    #     return True
    
    # def validate_file_size(self, file, max_size_mb=10):
    #     """Validate kích thước file"""
    #     if not file:
    #         return False
            
    #     file.seek(0, 2)  # Seek to end
    #     size = file.tell()
    #     file.seek(0)     # Seek back to start
        
    #     max_size_bytes = max_size_mb * 1024 * 1024
    #     if size > max_size_bytes:
    #         self.add_error(f"File quá lớn. Kích thước tối đa: {max_size_mb}MB.")
    #         return False
            
    #     return True

   
# import re
# import pandas as pd
# class BaseValidator:
#     """
#     regex: [] 1 ký tự duy nhất
#     Khởi tạo bộ Validator tổng quát
#     - Danh sách các thuộc tính:
#         +data: dictionary chứa dữ liệu cần kiểm tra
#     - Các quy tắc kiểm tra:
#         - required: Kiểm tra trường bắt buộc
#         - max_length: Kiểm tra độ dài tối đa của trường
#         -unique_value: Kiểm tra trường bắt buộc
#         - emailcheck: Kiểm tra định dạng email
#         - facebookcheck: Kiểm tra định dạng facebook
#         - dobcheck: Kiểm tra định dạng ngày sinh
#         - hobbiescheck: Kiểm tra dữ liệu hobbies
#         - add_error: Thêm lỗi vào danh sách lỗi
#         - errors: Lưu trữ các lỗi đã xảy ra trong quá trình kiểm tra
#     """
#     def __init__(self, data=None, model = None):
#         self.data = data or {}  
#         self.errors = {}
#         self.model = model
#         self.rules = {}
#         self.define_rules()

#     def get_errors(self):
#         return self.errors
    
#     def add_error(self, message):
#         if message:
#             self.errors.append(message)

#     def required(self, field):
#         value = self.data.get(field)
#         if value is None or str(value).strip() == "":
#             self.add_error(f"{field} là bắt buộc.")

#     def max_length(self, field, max_length):
#         value = self.data.get(field)
#         if isinstance(value, str):
#             value = value.strip()
#         elif value is not None:
#             value = str(value).strip()
#         else:
#             value = ""

#         if len(value) > max_length:
#             self.add_error(f"{field} tối đa {max_length} ký tự.")


#     def unique_value(self, field, model, except_id = None):
#         value = self.data.get(field)
#         if value is None:
#             return 
#         value = str(value).strip()
#         domain = [(field, '=', value)]
#         if except_id:
#             domain.append(('id', '!=', except_id))
#         if model.search(domain, limit = 1):
#             self.add_error(f" {field} đã tồn tại.")
            
#     def emailcheck(self, field):
#         value = self.data.get(field, '')
#         regex_email = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,7}\b'
#         if value and not re.match(regex_email, value):
#             self.add_error("Email không đúng định dạng.")
    
#     def facebookcheck(self, field):
#         value = self.data.get(field, '')
#         regex_facebook = r'^(https?:\/\/)?(www\.)?facebook\.com\/[A-Za-z0-9\.]+\/?$'
#         if value and not re.match(regex_facebook, value):
#             self.add_error("Facebook không đúng định dạng.")
        
#     def dobcheck(self, field):
#         value = self.data.get(field, '')
#         regex_dob = r'^\d{4}\-(0?[1-9]|1[012])\-(0?[1-9]|[12][0-9]|3[01])$'
#         if value  and not re.match(regex_dob, value):
#             self.add_error("Ngày sinh không đúng định dạng.")
            
#     def hobbiescheck(self, field):
#         value = self.data.get(field)
#         if not isinstance(value, str) or len(value) != 57:
#             self.add_error("Hobbies phải là ký tự có độ dài 57.")
#         else :
#             regex_hobbies =  r'^(0|1)(,(0|1)){28}$'
#             if value and not re.match(regex_hobbies, value):
#                 self.add_error("Hobbies không đúng định dạng.")
        
   
    
#     def validate_file_content(self, file):
#         """Validate nội dung file và trả về DataFrame"""
#         if not self.validate_file_format(file) or not self.validate_file_size(file):
#             return None
            
#         try:
#             filename = file.filename.lower()
#             file.seek(0)
            
#             if filename.endswith('.csv'):
#                 content = file.stream.read().decode('utf-8-sig')
#                 df = pd.read_csv(io.StringIO(content))
#             elif filename.endswith(('.xlsx', '.xls')):
#                 df = pd.read_excel(file.stream)
#             else:
#                 self.add_error("Định dạng file không được hỗ trợ.")
#                 return None
                
#             if df.empty:
#                 self.add_error("File không chứa dữ liệu.")
#                 return None
                
#             return df
            
#         except Exception as e:
#             self.add_error(f"Lỗi đọc file: {str(e)}")
#             return None
   