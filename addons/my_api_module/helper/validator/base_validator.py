import re
import pandas as pd
import io

class BaseValidator:
    def __init__(self, data=None, model=None):
        self.data = data or {}  
        self.errors = {}
        self.model = model
        self.create_rules = {}
        self.update_rules = {}
        self._define_rules()

    def _define_rules(self):
        """Override trong subclass để định nghĩa rules"""
        pass

    def define_create_rules(self, rules):
        """Định nghĩa rules cho CREATE operation"""
        self.create_rules = rules

    def define_update_rules(self, rules):
        """Định nghĩa rules cho UPDATE operation"""
        self.update_rules = rules

    def get_errors(self):
        return self.errors
    
    def clear_errors(self):
        self.errors = {}
        
    def add_error(self, field, message):
        if field not in self.errors:
            self.errors[field] = []
        self.errors[field].append(message)

    def validate_with_rules(self, rules, fields_to_validate=None):
        """Validate với rules được chỉ định"""
        self.errors = {}
        
        # Nếu không chỉ định fields, validate tất cả
        if fields_to_validate is None:
            fields_to_validate = rules.keys()
        
        for field_name in fields_to_validate:
            if field_name in rules:
                self._validate_field(field_name, rules[field_name])

    def _validate_field(self, field_name, field_rules):
        """Validate một field theo rules"""
        for rule in field_rules:
            self._apply_rule(field_name, rule)

    def _apply_rule(self, field_name, rule):
        """Apply một rule cụ thể"""
        # Parse rule string
        if ':' in rule:
            rule_type, rule_value = rule.split(':', 1)
        else:
            rule_type = rule
            rule_value = None
            
        # Apply rule based on type
        if rule_type == 'required':
            self._check_required(field_name)
        elif rule_type == 'max_length':
            self._check_max_length(field_name, int(rule_value))
        elif rule_type == 'unique_value':
            except_id = int(rule_value) if rule_value else None
            self._check_unique(field_name, except_id)
        elif rule_type == 'email':
            self._check_email(field_name)
        elif rule_type == 'facebook':
            self._check_facebook(field_name)
        elif rule_type == 'dob':
            self._check_dob(field_name)
        elif rule_type == 'hobbies':
            self._check_hobbies(field_name)

    # Validation methods (giữ nguyên như cũ)
    def _check_required(self, field):
        value = self.data.get(field)
        if value is None or str(value).strip() == "":
            self.add_error(field, f"{field} bắt buộc phải có.")

    def _check_max_length(self, field, max_length):
        value = self.data.get(field)
        if value is None:
            return
            
        value_str = str(value).strip()
        if len(value_str) > max_length:
            self.add_error(field, f"{field} tối đa {max_length} ký tự.")

    def _check_unique(self, field, except_id=None):
        value = self.data.get(field)
        if value is None or not str(value).strip():
            return 
            
        value = str(value).strip()
        domain = [(field, '=', value)]
        if except_id:
            domain.append(('id', '!=', except_id))
        if self.model.search(domain, limit=1):
            self.add_error(field, f"{field} đã tồn tại.")
            
    def _check_email(self, field):
        value = self.data.get(field, '')
        if not value:
            return
            
        regex_email = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,7}\b'
        if not re.match(regex_email, value):
            self.add_error(field, "Email không đúng định dạng.")
    
    def _check_facebook(self, field):
        value = self.data.get(field, '')
        if not value:
            return
            
        regex_facebook = r'^(https?:\/\/)?(www\.)?facebook\.com\/[A-Za-z0-9\.]+\/?$'
        if not re.match(regex_facebook, value):
            self.add_error(field, "Facebook không đúng định dạng.")
        
    def _check_dob(self, field):
        value = self.data.get(field, '')
        if not value:
            return
            
        regex_dob = r'^\d{4}\-(0?[1-9]|1[012])\-(0?[1-9]|[12][0-9]|3[01])$'
        if not re.match(regex_dob, value):
            self.add_error(field, "Ngày sinh không đúng định dạng.")
            
    def _check_hobbies(self, field):
        value = self.data.get(field)
        if not value:
            return
            
        if not isinstance(value, str) or len(value) != 57:
            self.add_error(field, "Hobbies phải là ký tự có độ dài 57.")
        else:
            regex_hobbies = r'^(0|1)(,(0|1)){28}$'
            if not re.match(regex_hobbies, value):
                self.add_error(field, "Hobbies không đúng định dạng.")

    def has_errors(self):
        return len(self.errors) > 0

    def validate_create_data(self, data):
        """Validate cho CREATE - tất cả fields với create_rules"""
        self.data = data
        self.validate_with_rules(self.create_rules)
        return self.get_errors()

    def validate_update_data(self, data, entity_id):
        """Validate cho UPDATE - chỉ fields có trong data với update_rules"""
        self.data = data
        
        # Update unique_value rules với except_id
        self._prepare_update_rules(entity_id)
        
        # Chỉ validate fields có trong data
        fields_to_validate = data.keys()
        self.validate_with_rules(self.update_rules, fields_to_validate)
        return self.get_errors()

    def _prepare_update_rules(self, entity_id):
        """Chuẩn bị update rules với except_id cho unique validation"""
        for field_name, field_rules in self.update_rules.items():
            for i, rule in enumerate(field_rules):
                if rule == 'unique_value':
                    self.update_rules[field_name][i] = f'unique_value:{entity_id}'
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
#         - email_check: Kiểm tra định dạng email
#         - facebook_check: Kiểm tra định dạng facebook
#         - dob_check: Kiểm tra định dạng ngày sinh
#         - hobbies_check: Kiểm tra dữ liệu hobbies
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
            
#     def email_check(self, field):
#         value = self.data.get(field, '')
#         regex_email = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,7}\b'
#         if value and not re.match(regex_email, value):
#             self.add_error("Email không đúng định dạng.")
    
#     def facebook_check(self, field):
#         value = self.data.get(field, '')
#         regex_facebook = r'^(https?:\/\/)?(www\.)?facebook\.com\/[A-Za-z0-9\.]+\/?$'
#         if value and not re.match(regex_facebook, value):
#             self.add_error("Facebook không đúng định dạng.")
        
#     def dob_check(self, field):
#         value = self.data.get(field, '')
#         regex_dob = r'^\d{4}\-(0?[1-9]|1[012])\-(0?[1-9]|[12][0-9]|3[01])$'
#         if value  and not re.match(regex_dob, value):
#             self.add_error("Ngày sinh không đúng định dạng.")
            
#     def hobbies_check(self, field):
#         value = self.data.get(field)
#         if not isinstance(value, str) or len(value) != 57:
#             self.add_error("Hobbies phải là ký tự có độ dài 57.")
#         else :
#             regex_hobbies =  r'^(0|1)(,(0|1)){28}$'
#             if value and not re.match(regex_hobbies, value):
#                 self.add_error("Hobbies không đúng định dạng.")
        
#     def validate_file_format(self, file):
#         """Validate định dạng file"""
#         if not file or not hasattr(file, 'filename') or not file.filename:
#             self.add_error("File không hợp lệ hoặc không có tên.")
#             return False
            
#         filename = file.filename.lower()
#         allowed_extensions = ['.csv', '.xlsx', '.xls']
        
#         if not any(filename.endswith(ext) for ext in allowed_extensions):
#             self.add_error("Chỉ hỗ trợ file CSV (.csv) hoặc Excel (.xlsx, .xls).")
#             return False
            
#         return True
    
#     def validate_file_size(self, file, max_size_mb=10):
#         """Validate kích thước file"""
#         if not file:
#             return False
            
#         file.seek(0, 2)  # Seek to end
#         size = file.tell()
#         file.seek(0)     # Seek back to start
        
#         max_size_bytes = max_size_mb * 1024 * 1024
#         if size > max_size_bytes:
#             self.add_error(f"File quá lớn. Kích thước tối đa: {max_size_mb}MB.")
#             return False
            
#         return True
    
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
   