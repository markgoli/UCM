import uuid
import base64
import os

def generate_bs64_slug():
    uid_bytes = uuid.uuid4().bytes
    random_bytes = os.urandom(20)
    slug = base64.urlsafe_b64encode(uid_bytes + random_bytes).decode().rstrip("=")
    return slug


def generate_archive_id():
    uid_bytes = uuid.uuid4().bytes
    # Encode to URL-safe Base64, strip padding '='
    archive_id = base64.urlsafe_b64encode(uid_bytes).decode().rstrip("=")

    return archive_id