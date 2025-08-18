import pandas as pd
import io
from odoo.http import Response
from io import StringIO
import numpy as np


def export_file(data, file_name, type='csv'):
    print(type)
    output = io.StringIO()

    if type == 'csv':
        pd.DataFrame(data).to_csv(output, index=False)
    elif type == 'xlsx':
        output = io.BytesIO()
        pd.DataFrame(data).to_excel(output, index=False)
    else:
        raise ValueError("Unsupported file type")

    return Response(
        output.getvalue(),
        headers={
            'Content-Disposition': f'attachment; filename={file_name}.{type}',
            'Content-Type': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' if type == 'xlsx' else 'text/csv'
        }
    )


def import_file(file):
    if not hasattr(file, 'read'):
        raise ValueError("File không hợp lệ")

    filename = file.filename.lower()

    try:
        file.seek(0)

        # Xử lý file CSV
        if filename.endswith('.csv'):
            content = file.read().decode('utf-8-sig')
            df = pd.read_csv(StringIO(content), encoding='utf-8-sig')

        # Xử lý file Excel (.xls hoặc .xlsx)
        elif filename.endswith(('.xls', '.xlsx')):
            df = pd.read_excel(file, engine='openpyxl')

        else:
            raise ValueError("Chỉ hỗ trợ file .csv, .xls, .xlsx")

        df = df.where(pd.notnull(df), None)

        df = df.replace({np.nan: None})

        # Trả về dữ liệu dạng list[dict]
        return df.to_dict(orient='records')

    except Exception as e:
        raise ValueError(f"Lỗi đọc file: {str(e)}")