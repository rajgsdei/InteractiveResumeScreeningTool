from symbol import except_clause

import pdfplumber
import docx
import re
import os
import traceback

from django.http import HttpResponse
from django.shortcuts import render
from django.core.files.storage import FileSystemStorage
from .models import Resume
from django.core.paginator import Paginator
from django.conf import settings

# Extract text from PDF
def extract_text_from_pdf(pdf_path):
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text() + "\n"
    return text.strip()

# Extract text from DOCX
def extract_text_from_docx(docx_path):
    doc = docx.Document(docx_path)
    return "\n".join([para.text for para in doc.paragraphs])

# Extract structured data (Name, Email, Phone, Skills)
def extract_resume_data(text):
    name = re.search(r"([A-Z][a-z]+\s[A-Z][a-z]+)", text)  # Basic regex for name
    email = re.search(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", text)
    phone = re.search(r"\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}", text)

    skills = ["Python", "Django", "Machine Learning", "AI", "JavaScript", "React", "SQL"]
    found_skills = [skill for skill in skills if skill.lower() in text.lower()]

    return {
        "name": name.group() if name else "Unknown",
        "email": email.group() if email else "Not Found",
        "phone": phone.group() if phone else "Not Found",
        "skills": found_skills,
        "education": text
    }


def home(request):
    return render(request, 'resume_screening/landing_page.html')

def about(request):
    return render(request, 'resume_screening/about.html')


def view_resumes(request):
    try:
        resumes_list = Resume.objects.all()

        # Set up pagination (show 10 resumes per page)
        paginator = Paginator(resumes_list, 10)  # Show 10 resumes per page
        page_number = request.GET.get('page')  # Get the current page from the query parameters
        page_obj = paginator.get_page(page_number)
        return render(request, 'resume_screening/view_resumes.html',
                      {'MEDIA_URL': settings.MEDIA_URL,'resumes': resumes_list, 'page_obj': page_obj})
    except Exception as e:
        error_message = traceback.format_exc()  # Capture the full traceback
        return HttpResponse(f"Database connection failed: {error_message}")


# Enhanced Upload Function (Keeps Your Existing Code, Adds Resume Parsing)
def upload(request):
    upload_message = ""
    upload_btn_text = "Upload"

    if request.method == 'POST' and request.FILES.get('resume'):
        resume = request.FILES['resume']

        # Define the relative directory where you want to save the file
        upload_dir = 'resume/'  # Save files inside the 'media/resume/' folder

        # Ensure the directory exists (relative to MEDIA_ROOT)
        upload_path = os.path.join(settings.MEDIA_ROOT, upload_dir)
        if not os.path.exists(upload_path):
            os.makedirs(upload_path)

        # Save the file to the specified directory using FileSystemStorage
        fs = FileSystemStorage(location=upload_path)  # Pass relative path for storage
        filename = fs.save(resume.name, resume)
        uploaded_file_url = fs.url(filename)  # URL that will be used for the file download link

        # Extract text based on file type
        if resume.name.endswith('.pdf'):
            text = extract_text_from_pdf(fs.path(filename))
        elif resume.name.endswith('.docx'):
            text = extract_text_from_docx(fs.path(filename))
        else:
            return render(request, 'resume_screening/upload_page.html', {'upload_message': 'Unsupported file format', 'upload_btn_text': upload_btn_text})

        # Extract structured resume data
        extracted_data = extract_resume_data(text)

        # Save structured data into MongoDB (or another storage)
        try:
            Resume.objects.create(
                name=extracted_data['name'],
                email=extracted_data['email'],
                phone=extracted_data['phone'],
                skills=extracted_data['skills'],
                education=extracted_data['education'],
                resume_file=filename  # Just the filename, no need for the full path
            )
        except Exception as e:
            print(f"An error occurred: {e}")

        # Provide feedback message for successful upload
        if upload_message == "":
            upload_message = f'Resume uploaded successfully! Extracted Name: {extracted_data["name"]}'
            upload_btn_text = "Upload next resume"
        else:
            upload_btn_text = "Upload"
            upload_message = ""

    return render(request, 'resume_screening/upload_page.html', {
        'upload_message': upload_message,
        'upload_btn_text': upload_btn_text
    })
