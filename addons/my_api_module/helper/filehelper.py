import pandas as pd
import io
from odoo.http import Response
from io import StringIO
from fpdf import FPDF
import numpy as np
import logging
_logger = logging.getLogger(__name__)


# def export_file(data, file_name, type='csv'):
#     print(type)
#     output = io.StringIO()

#     if type == 'csv':
#         pd.DataFrame(data).to_csv(output, index=False)
#     elif type == 'xlsx':
#         output = io.BytesIO()
#         pd.DataFrame(data).to_excel(output, index=False)

#     else:
#         raise ValueError("Unsupported file type")

#     return Response(
#         output.getvalue(),
#         headers={
#             'Content-Disposition': f'attachment; filename={file_name}.{type}',
#             'Content-Type': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' if type == 'xlsx' else 'text/csv'
#         }
#     )
def export_file(data, file_name, type='csv'):
    output = io.StringIO() if type == 'csv' else io.BytesIO()

    if type == 'csv':
        _logger.info(f"data là :{data}")
        pd.DataFrame(data).to_csv(output, index=False)
        content = output.getvalue()
        content_type = 'text/csv'
    elif type == 'xlsx':
        pd.DataFrame(data).to_excel(output, index=False)
        content = output.getvalue()
        content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    elif type == 'pdf':
        # Tạo file PDF đơn giản với FPDF
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        df = pd.DataFrame(data)
        # Header
        for col in df.columns:
            pdf.cell(40, 10, str(col), border=1)
        pdf.ln()
        # Rows
        for _, row in df.iterrows():
            for val in row:
                pdf.cell(40, 10, str(val), border=1)
            pdf.ln()
        pdf_bytes = pdf.output(dest='S').encode('latin1') 
        content = pdf_bytes
        content_type = 'application/pdf'
    else:
        raise ValueError("Không hỗ trợ file này")

    return Response(
        content,
        headers={
            'Content-Disposition': f'attachment; filename={file_name}.{type}',
            'Content-Type': content_type
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

        # Xử lý file Excel (.xls hoặc .xlsx, xml, odf)
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