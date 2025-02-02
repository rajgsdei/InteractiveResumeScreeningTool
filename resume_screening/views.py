from django.shortcuts import render
from django.http import HttpResponse
from django.core.files.storage import FileSystemStorage


def home(request):
    return render(request, 'resume_screening/landing_page.html')


def upload(request):
    upload_message = ""  # Variable to store the upload result message
    if request.method == 'POST' and request.FILES.get('resume'):
        # Handling the uploaded file
        resume = request.FILES['resume']
        fs = FileSystemStorage()
        filename = fs.save(resume.name, resume)
        uploaded_file_url = fs.url(filename)
        upload_message = f'File uploaded successfully! You can view it <a href="{uploaded_file_url}">here</a>.'

    return render(request, 'resume_screening/upload_page.html', {'upload_message': upload_message})
