from odoo import models, fields, api
from enum import Enum
class ClassAlias2Fields(Enum):
    id = 'id'
    co = 'code'
    na = 'name'
    de = 'description'
    # cd = 'create_date'
    # wr = 'write_date'
    # cu = 'create_uid'
    # wu = 'write_uid'


class ClassFields2Labels(Enum):
    id = "ID"
    code = "Ma Lop"
    name = "Ten Lop"
    description = "Mo ta"
    # create_date = 'Ngày tạo'
    # write_date = 'Ngày cập nhật'
    # create_uid = 'Mã Người tạo'
    # write_uid = 'Mã Người cập nhật' 

class Course(models.Model):
    _name = 'my_api_module.classes'
    _description = 'Class'
    _rec_name = 'name'

    code = fields.Char(string='Course Code',size = 100, default = None, required=True, help = "Mã lớp học, ví dụ: LOP001")
    name = fields.Char(string='Course Name',size = 100, default = None, required=True, help = "Tên lớp học, ví dụ: Lớp 10A1")
    description = fields.Text(string='Description', required = False)
    # write_date = fields.Datetime(string='Last Updated') 

    student_ids = fields.One2many('my_api_module.student', 'class_id', string='Students')
    
  