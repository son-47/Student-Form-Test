from ..helper.password_processor import PasswordHelper
import logging

_logger = logging.getLogger(__name__)

class DataProcessor:
    """Xử lý  logic sau khi data đã được validated"""
    
    def __init__(self, entity_type):
        self.entity_type = entity_type
    
    def process_for_create(self, data):
        """Process data trước khi create"""
        processed_data = data.copy()
        
        if self.entity_type == 'student':
            processed_data = self.process_student_create(processed_data)
        elif self.entity_type == 'classes':
            processed_data = self.process_class_create(processed_data)
        
        return processed_data
    
    def process_for_update(self, data):
        """Process data trước khi update"""
        processed_data = data.copy()
        
        if self.entity_type == 'student':
            processed_data = self.process_student_update(processed_data)
        elif self.entity_type == 'classes':
            processed_data = self.process_class_update(processed_data)
        
        return processed_data
    
    def process_for_import(self, data_list):
        """Process data list từ import"""
        processed_list = []
        
        for record in data_list:
            if self.entity_type == 'student':
                processed_record = self.process_student_import(record.copy())
            elif self.entity_type == 'classes':
                processed_record = self.process_class_import(record.copy())
            else:
                processed_record = record.copy()
                
            processed_list.append(processed_record)
        
        return processed_list
    
    # Student-specific processing
    def process_student_create(self, data):
        """Process student data for create"""
        # Hash password
        if 'password' in data:
            data['password'] = PasswordHelper.hash_password(data['password'])
        
        # Encode hobbies
        if 'hobbies' in data:
            data['hobbies'] = self._encode_hobbies_bitmask(data['hobbies'])
        
        return data
    
    def process_student_update(self, data):
        """Process student data for update"""
        # Hash password only if provided
        if 'password' in data:
            data['password'] = PasswordHelper.hash_password(data['password'])
        
        # Encode hobbies
        if 'hobbies' in data:
            data['hobbies'] = self._encode_hobbies_bitmask(data['hobbies'])
        
        return data
    
    def process_student_import(self, data):
        """Process student data for import"""
        # Convert sex to string
        if 'sex' in data:
            data['sex'] = str(data.get('sex'))
        
        # Hash password
        if 'password' in data and data['password']:
            data['password'] = PasswordHelper.hash_password(data['password'])
        
        # Encode hobbies
        if 'hobbies' in data:
            data['hobbies'] = self._encode_hobbies_bitmask(data['hobbies'])
        
        return data
    
    # Class-specific processing (minimal)
    def process_class_create(self, data):
        return data
    
    def process_class_update(self, data):
        return data
    
    def process_class_import(self, data):
        return data
    
    # Helper methods
    def _encode_hobbies_bitmask(self, hobbies_input):
        """Encode hobbies to bitmask"""
        if not hobbies_input or hobbies_input.strip() == "":
            return 0
        
        bits = list(map(int, hobbies_input.strip().split(',')))
        bitmask = 0 
        for i, value in enumerate(bits):
            if value == 1:
                bitmask |= (1 << i)
        return bitmask