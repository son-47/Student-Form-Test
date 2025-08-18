import json
from odoo.http import Response


class ErrorFormat(Exception):
    """
    Khởi tạo bộ lỗi theo định dạng chuẩn theo yêu cầu
    - Danh sách các thuộc tính:
        + code: Mã lỗi
        + status: Trạng thái của lỗi (thành công, thất bại, lỗi)
        + message: Thông điệp mô tả lỗi
        + data: Dữ liệu trả về (nếu có)
        + old_data: Dữ liệu cũ (nếu có)
    - Các thương thức:
        + get_response: Trả về một đối tượng Response chứa thông tin lỗi dưới dạng JSON
    """

    def __init__(self, code, status, message, data=None, old_data=None):
        self.code = code
        self.status = status
        self.message = message
        self.data = data
        self.old_data = old_data

    def get_response(self):
        return Response(json.dumps({
            'code': self.code,
            'status': self.status,
            'message': self.message,
            'old_data': self.old_data,
            'data': self.data
        }),
            status=200,
            content_type='application/json'
        )