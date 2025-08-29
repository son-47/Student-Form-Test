FROM odoo:18.0

USER root

RUN apt-get update && \
    apt-get install -y python3-pip && \
    pip3 install --no-cache-dir --break-system-packages \
        python-docx pandas openpyxl minio bcrypt fpdf PyJWT \
        google-auth google-auth-oauthlib google-auth-httplib2 \
        requests-oauthlib && \
    apt-get clean

USER odoo