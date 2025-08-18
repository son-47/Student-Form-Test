import json
from odoo.http import Response

# def get_response(data):
#     return Response(json.dumps({
#         'code': '200',
#         'status': 'success',
#         'message': 'Thành công',
#         'data': data
#     },ensure_ascii = False),
#         status=200,
#         content_type='application/json'
#     )
    
def responseFormat(code, message = None, data=None):
    res = {}
    res['code'] = code
    if (code == 200):
        res['status'] = 'success'
        res['message'] = 'Thành công'
    else:
        res['status'] = 'error'
    if message:
        res['message'] = message
    res['data'] = data if data is not None else {}
    return Response(json.dumps(res, ensure_ascii=False), status=200, content_type='application/json')
