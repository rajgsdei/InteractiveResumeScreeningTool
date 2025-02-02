# utilities/save_file.py
from django.core.files.storage import FileSystemStorage
import os
from django.conf import settings

def save_uploaded_file(file):
    upload_dir = 'resume/'  # Directory to save files
    upload_path = os.path.join(settings.MEDIA_ROOT, upload_dir)

    # Ensure the directory exists
    if not os.path.exists(upload_path):
        os.makedirs(upload_path)

    # Use Django's FileSystemStorage to save the file
    fs = FileSystemStorage(location=upload_path)
    filename = fs.save(file.name, file)
    uploaded_file_url = fs.url(filename)

    return filename, uploaded_file_url
