from .base_validator import BaseValidator

class ClassValidator(BaseValidator):
    def __init__(self, data=None, model=None):
        super().__init__(data, model)

    def _define_rules(self):
        """Định nghĩa rules khác nhau cho CREATE và UPDATE"""
        
        # CREATE RULES - Tất cả field bắt buộc
        self.define_create_rules({
            "code": ["required", "unique_value", "max_length:50"],
            "name": ["required", "unique_value", "max_length:100"],
            "description": ["max_length:200"]
        })
        
        # UPDATE RULES - Không required, chỉ validation
        self.define_update_rules({
            "code": ["unique_value", "max_length:50"],    # Không required
            "name": ["unique_value", "max_length:100"],   # Không required  
            "description": ["max_length:200"]
        })
        
    # def constraint_validate(self):
    #     self.required('code')
    #     self.required('name')

    # def validate_data(self):
    #     self.max_length('code', 100)
    #     self.max_length('name', 100)

    # def validate_create_data(self, data):
    #     self.data = data
    #     self.unique_value('code', self.model)
    #     self.constraint_validate()
    #     self.validate_data()
    #     return self.get_errors()

    # def validate_update_data(self, data, id):
    #     self.data = data
    #     self.validate_data()
    #     self.unique_value('code', self.model, id)
    #     return self.get_errors()

    # def validate_import_file(self, file):
    #     """Validate file import lớp học - TẬN DỤNG CÁC HÀM CÓ SẴN"""
    #     self.errors = []
        
    #     # Validate định dạng và nội dung
    #     df = self.validate_file_content(file)
    #     if df is None:
    #         return None, []
        
    #     # Validate cột bắt buộc
    #     required_columns = ['code', 'name']
    #     if not self.validate_required_columns(df, required_columns):
    #         return None, []
        
    #     # Validate từng dòng 
    #     # valid_records = self.validate_data_rows(df, self._validate_class_row)
        
    #     return df, valid_records
    
    # def validate_update_file(self, file):
    #     """Validate file update lớp học"""
    #     self.errors = []
        
    #     # Validate file
    #     df = self.validate_file_content(file)
    #     if df is None:
    #         return None
        
    #     if len(df) != 1:
    #         self.add_error("File cập nhật chỉ được chứa đúng 1 dòng dữ liệu.")
    #         return None
        
    #     # Extract data
    #     row_data = df.iloc[0].to_dict()
    #     clean_data = {}
    #     for k, v in row_data.items():
    #         if pd.notna(v) and v is not None:
    #             clean_data[k] = str(v).strip() if isinstance(v, str) else v
        
    #     # Validate với các hàm có sẵn
    #     temp_data = self.data
    #     self.data = clean_data
        
    #     self._validate_class_fields_update()
        
    #     self.data = temp_data
        
    #     return clean_data if not self.errors else None
    
    # def _validate_class_row(self, row_data, row_number):
    #     """Validate một dòng lớp học"""
    #     # Backup và set data mới
    #     temp_data = self.data
    #     temp_errors = self.errors
        
    #     self.data = row_data
    #     self.errors = []
        
    #     self.constraint_validate()  
    #     self.validate_data()        
        
    #     row_errors = self.errors.copy()
        
    #     # Restore
    #     self.data = temp_data
    #     self.errors = temp_errors
        
    #     return row_errors
    
    # def _validate_class_fields_update(self):
    #     """Validate fields cho update """
    #     # Max length 
    #     if self.data.get('code'):
    #         self.max_length('code', 50)
    #     if self.data.get('name'):
    #         self.max_length('name', 100)
    #     if self.data.get('description'):
    #         self.max_length('description', 200)
        
    #     # Unique 
    #     if self.data.get('code'):
    #         self.unique_value('code', self.model)
    #     if self.data.get('name'):
    #         self.unique_value('name', self.model)
