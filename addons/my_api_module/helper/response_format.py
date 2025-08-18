import json
from odoo.http import Response


def get_response(data):
    return Response(json.dumps({
        'code': '200',
        'status': 'success',
        'message': 'Thành công',
        'data': data
    }),
        status=200,
        content_type='application/json'
    )

def responseFormat(code, message = None, data=None, oldData = None):
    res = {}
    res['code'] = code
    if (code == 200):
        res['status'] = 'success'
    else:
        res['status'] = 'error'
    if message:
        res['message'] = message
    if oldData:
        res['data'] = {'old_data': oldData, 'error': data}
    elif data:
        res['data'] = data
    return Response(json.dumps(res), status = 200, content_type='application/json')
    