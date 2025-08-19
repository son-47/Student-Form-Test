from odoo import models, fields
from enum import Enum 
class StudentAlias2Fields(Enum):
    id = 'id'
    co = 'code'
    fu = 'fullname'
    dob = 'dob'
    sex = 'sex'
    hc = 'homecity'
    addr = 'address'
    hb = 'hobbies'
    hair = 'hair_color'
    em = 'email'
    fb = 'facebook'
    un = 'username'
    pw = 'password'
    de = 'description'
    att = 'attachment'
    att_url = 'attachment_url'

    # cd = 'create_date'
    # wr = 'write_date'
    # cu = 'create_uid'
    # wu = 'write_uid'


class StudentFields2Labels(Enum):
    id = "ID"
    code = "Ma hoc Sinh"
    fullname = "Ten hoc sinh"
    dob = "Ngay sinh"
    sex = "Gioi tinh"
    homecity = "Que quan"
    address = "Dia chi"
    hobbies = "So thich"
    hair_color = "Mau toc"
    email = "Email"
    facebook = "Facebook"
    username = "Ten dang nhap"
    password = "Mat khau"
    description = "Mo ta"
    attachment = "Duong dan anh"
    attachment_url = "Link anh"
    # create_date = 'Ngày tạo'
    # write_date = 'Ngày cập nhật'
    # create_uid = 'Mã Người tạo'
    # write_uid = 'Mã Người cập nhật' 

class Student(models.Model):
    _name = 'my_api_module.student'
    _description = 'Student'
    _rec_name = 'fullname'

    code = fields.Char(string='Student Code',size = 50,  required=True)            
    fullname = fields.Char(string='Full Name',size = 100, required=True)           
    dob = fields.Date(string='Date of Birth', required = True)                          
    sex = fields.Selection([                                            
        ('2', 'Female'),
        ('1', 'Male')
    ], string='Gender', required=True, default='1')  # Mặc định là Nam
    homecity = fields.Char(string='Hometown')                           # Tỉnh thành
    address = fields.Char(string='Address')                             # Địa chỉ chi tiết
    hobbies = fields.Integer(string='Hobbies')                             # Danh sách sở thích (chuỗi 0,1,...)
    hair_color = fields.Char(string='Hair Color')                       # Màu tóc
    email = fields.Char(string='Email', required = True)                                 # Email liên hệ
    facebook = fields.Char(string='Facebook')                                          # Link Facebook
    username = fields.Char(string='Username',required= True)                           # Tên tài khoản
    password = fields.Char(string='Password', size =255, required = True)                           # Mật khẩu 
    description = fields.Text(string='Description')   
 # Ghi chú
    attachment = fields.Char(string='Attachment')                     # File đính kèm (ảnh/hồ sơ)
    attachment_url = fields.Char(string='Attachment URL')  # URL của file đính kèm
    
    # file_name = fields.Char("Tên file gốc")
    # file_path = fields.Char("Đường dẫn lưu ảnh")
    class_id = fields.Many2one('my_api_module.classes', string='Class')   # Môn học / lớp
   