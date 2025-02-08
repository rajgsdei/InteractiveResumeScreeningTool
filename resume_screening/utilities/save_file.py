from django.core.files.storage import FileSystemStorage
import os
from django.conf import settings
from datetime import datetime

def save_uploaded_file(file):
    upload_dir = 'resume/'  # Directory to save files
    upload_path = os.path.join(settings.MEDIA_ROOT, upload_dir)

    # Ensure the directory exists
    if not os.path.exists(upload_path):
        os.makedirs(upload_path)

    # Generate a unique filename by appending the current timestamp including milliseconds
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S') + f"_{datetime.now().microsecond // 1000:03d}"
    name, extension = os.path.splitext(file.name)
    unique_filename = f"{name}_{timestamp}{extension}"

    # Use Django's FileSystemStorage to save the file with the new filename
    fs = FileSystemStorage(location=upload_path)
    filename = fs.save(unique_filename, file)  # Save with the unique filename
    uploaded_file_url = fs.url(filename)  # Get the URL for the uploaded file

    return filename, uploaded_file_url
