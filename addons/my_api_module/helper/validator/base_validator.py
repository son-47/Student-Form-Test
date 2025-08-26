import re
import pandas as pd
import io
from odoo.http import request, Response

class BaseValidator():
    URL_PATTERNS = {
    'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,7}\b',
    'facebook': r'^(https?:\/\/)?(www\.)?facebook\.com\/[A-Za-z0-9\.]+\/?$',
}
    def __init__(self, data=None, model=None, modelFields2Labels=None):
        self.data = data or {}  
        self.errors = {}
        self.model = model
        self.modelFields2Labels = modelFields2Labels

        self.rules = {}
        self.messages = self.get_default_messages()
        self.define_rules()


    def define_rules(self):
        """định nghĩa rules"""
        pass

    def define_field_rules(self, rules):
        """Định nghĩa rules cho từng field"""
        self.rules = rules
        
    def get_default_messages(self):
        """Định nghĩa message"""
        return {
            'required': '{} không được để trống.',
            'unique': '{} đã tồn tại.',
            'max_length': '{0} tối đa {1} ký tự.',
            'min_length': '{0} tối thiểu {1} ký tự.',
            'max': '{0} không được vượt quá {1}',
            'min': '{0} không được nhỏ hơn {1}',
            'url': '{} không đúng định dạng url.',
            'date': '{} không đúng định dạng date.',
            'list': '{} không đúng định dạng list.',
            'number': '{} phải là số thực.',
            'file_size' : '{} vượt quá kích thước cho phép {}MB.',
            'file_name': '{} không đúng định dạng file. Chỉ hỗ trợ: {}.'
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
    
    
    def validate_field(self, field_name, field_rules, command='create', entity_id=None):
        """Validate một field theo rules"""
        field_label = self.get_field_label(field_name)
        
        for rule_type, rule_config in field_rules.items():
            if not rule_config:  # Skip nếu rule = False hoặc None
                continue
                
            # Skip required validation cho update command
            if rule_type == 'required' and command == 'update':
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
            
        elif rule_type == 'url' and rule_config:
            self.check_url(field_name, field_label)
            
        # elif rule_type == 'facebook' and rule_config:
        #     self.check_url(field_name, field_label)
            
        elif rule_type == 'date' and rule_config:
            self.check_date(field_name, field_label)   
        elif rule_type == 'list' and rule_config:
            self.check_list(field_name, field_label)
        elif rule_type == 'number' and rule_config:
            self.check_number(field_name, field_label)
        elif rule_type == 'file_size' and rule_config:
            self.check_file_size(field_name, field_label, rule_config)
        elif rule_type == 'file_name' and rule_config:
            self.check_file_name(field_name, field_label)
    # Validation methods
    def check_required(self, field, field_label):
        value = self.data.get(field)
        if value is None or str(value).strip() == "":
            message = self.messages['required'].format(field_label)
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
            message = self.messages['unique'].format(field_label)
            self.add_error(field, message)

    def check_max_length(self, field, field_label, max_length):
        value = self.data.get(field)
        if value is None:
            return
            
        value_str = str(value).strip()
        if len(value_str) > max_length:
            message = self.messages['max_length'].format(field_label, max_length)
            self.add_error(field, message)

    def check_min_length(self, field, field_label, min_length):
        value = self.data.get(field)
        if value is None:
            return
        value_str =str(value).strip()
        if len(value_str) < min_length:
            message = self.messages['min_length'].format(field_label, min_length)
            self.add_error(field, message)

  

    def check_min(self, field, field_label, min_value):
        value = self.data.get(field)
        if value is None:
            return
        value = float(value)
        if value < min_value:
            message = self.messages['min'].format(field_label, min_value)
            self.add_error(field, message)

    def check_max(self, field, field_label, max_value):
        value = self.data.get(field)
        if value is None:
            return
        value = float(value)
        if value > max_value:
            message = self.messages['max'].format(field_label, max_value)
            self.add_error(field, message)


    
    def check_number(self, field, field_label):
        value = self.data.get(field)
        if value is None:
            return
        if not isinstance(value, float):
            message = self.messages['number'].format(field_label)
            self.add_error(field, message)
        

    def check_url(self, field, field_label):
        value = self.data.get(field, '')
        if not value:
            return
        regex_url = self.URL_PATTERNS.get(field)
        if not re.match(regex_url, value):
            message = self.messages['url'].format(field_label)
            self.add_error(field, message)
    def check_date(self, field, field_label):
        value = self.data.get(field, '')
        if not value:
            return
        regex_date = r'^\d{4}\-(0?[1-9]|1[012])\-(0?[1-9]|[12][0-9]|3[01])$'
        if not re.match(regex_date, value):
            message = self.messages['date'].format(field_label)
            self.add_error(field, message)

    def check_list(self, field, field_label):
        value = self.data.get(field)
        if not value :
            return
                
        if not isinstance(value, str) or len(value) != 57:
            message = self.messages['list'].format(field_label)
            self.add_error(field, message)
        else:
            regex_list = r'^(0|1)(,(0|1)){28}$'
            if not re.match(regex_list, value):
                message = self.messages['list'].format(field_label)
                self.add_error(field, message)

    # def check_file_name(self, field, field_label):
    #     """Kiểm tra đuôi file theo field"""
    #     if not hasattr(request, 'httprequest') or not request.httprequest.files:
    #         return 
            
    #     file = request.httprequest.files.get(field)
    #     if not file or not file.filename:
    #         return  
        
    #     # Định nghĩa extensions theo field name
    #     field_extensions = {
    #         'fattachment': ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp', 'svg'],  # Chỉ image files
    #         'attachment': ['csv', 'xlsx', 'xls', 'xml', 'jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp', 'svg']  # Import files + image paths
    #     }
        
    #     allowed_extensions = field_extensions.get(field, [])
    #     if not allowed_extensions:
    #         return  
        
    #     ext = file.filename.lower().split('.')[-1] if '.' in file.filename else ''
    #     if ext not in allowed_extensions:
    #         extensions_str = ', '.join(allowed_extensions)
    #         message = self.messages['file_name'].format(field_label, extensions_str)
    #         self.add_error(field, message)
    def check_file_name(self, field, field_label):
        """Kiểm tra đuôi file theo field - CHỈ CHO CRUD operations"""
        if not hasattr(request, 'httprequest') or not request.httprequest.files:
            return 
            
        file = request.httprequest.files.get(field)
        if not file or not file.filename:
            return  
        
        # Định nghĩa extensions theo field name
        if field == 'fattachment':
            # fattachment luôn là image files
            allowed_extensions = ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp', 'svg']
        elif field == 'attachment':
            # attachment trong CRUD context - có thể là image path cho student
            # Detect entity type từ model name
            if '/update' in request.httprequest.path:
                # Student context - attachment có thể là image path
                allowed_extensions = ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp', 'svg']
            else:
                # Class hoặc entities khác - attachment là document
                allowed_extensions = ['csv', 'xlsx', 'xls']
        else:
            # Không có config thì bỏ qua
            return
        
        ext = file.filename.lower().split('.')[-1] if '.' in file.filename else ''
        if ext not in allowed_extensions:
            extensions_str = ', '.join(allowed_extensions)
            message = self.messages['file_name'].format(field_label, extensions_str)
            self.add_error(field, message)
    def check_file_size(self, field, field_label, max_size_mb):
        """Kiểm tra kích thước file"""
        if not hasattr(request, 'httprequest') or not request.httprequest.files:
            return  # Không có file thì bỏ qua
            
        file = request.httprequest.files.get(field)
        if not file or not file.filename:
            return  # Không có file thì bỏ qua

        file.seek(0, 2)  # ĐI đến cuối file
        size = file.tell()
        file.seek(0)     
        
        max_size_bytes = max_size_mb * 1024 * 1024
        if size > max_size_bytes:
            message = self.messages['file_size'].format(field_label, max_size_mb)
            self.add_error(field, message)
                    
    
    def validate_create_data(self, data):
        """Validate cho CREATE - tất cả fields có rules"""
        self.data = data
        self.errors = {}
        
        for field_name, field_rules in self.rules.items():
            self.validate_field(field_name, field_rules, command='create')
            
        return self.get_errors()

    def validate_update_data(self, data, entity_id = None):
        """Validate chỉ fields có trong data (update, import)"""
        self.data = data
        self.errors = {}
        
        # Validate fields trong data
        for field_name in data.keys():
            if field_name in self.rules:
                self.validate_field(field_name, self.rules[field_name], command='update', entity_id=entity_id)                    
        return self.get_errors()            

