import os
import uuid
import firebase_admin
from firebase_admin import credentials, storage

_initialized = False


def initialize_firebase():
    global _initialized

    if _initialized:
        return

    service_account_path = os.getenv("FIREBASE_SERVICE_ACCOUNT")
    bucket_name = os.getenv("FIREBASE_BUCKET")

    if not service_account_path:
        raise ValueError("FIREBASE_SERVICE_ACCOUNT is not set.")

    if not bucket_name:
        raise ValueError("FIREBASE_BUCKET is not set.")

    if not firebase_admin._apps:
        cred = credentials.Certificate(service_account_path)
        firebase_admin.initialize_app(cred, {
            "storageBucket": bucket_name
        })

    _initialized = True


def upload_pdf_to_firebase(file_storage, course_id):
    initialize_firebase()

    if not file_storage:
        raise ValueError("No file provided.")

    filename = file_storage.filename or "uploaded.pdf"
    unique_name = f"{uuid.uuid4()}_{filename}"
    blob_path = f"courses/{course_id}/files/{unique_name}"

    bucket = storage.bucket()
    blob = bucket.blob(blob_path)

    file_storage.seek(0)
    blob.upload_from_file(file_storage, content_type="application/pdf")

    blob.make_public()

    return {
        "filename": filename,
        "storage_path": blob_path,
        "url": blob.public_url
    }