from symbol import except_clause

import pdfplumber
import docx
import re
import os
import traceback
import random

from .utilities.save_file import save_uploaded_file
from django.http import HttpResponse, JsonResponse
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
    education = re.findall(
        r"(Bachelor['’]?\s?(of\s[A-Za-z]+|\w+)\s?[A-Za-z]+|Master['’]?\s?(of\s[A-Za-z]+|\w+)\s?[A-Za-z]+|PhD\s?[A-Za-z]*|Associate['’]?\s?[A-Za-z]+|[A-Za-z]+\sDegree|University[\sA-Za-z]+|College[\sA-Za-z]+)[^\n]*",
        text, re.IGNORECASE)

    education = [' '.join(filter(None, edu)).strip() for edu in education]

    skills = ["Python", "Django", "Machine Learning", "AI", "JavaScript", "React", "SQL"]
    found_skills = [skill for skill in skills if skill.lower() in text.lower()]

    applied_for = re.search(r"Applied\s*for[:\s]*(.*)", text, re.IGNORECASE)
    applied_for = applied_for.group(1).strip() if applied_for else "Not Found"

    experience = re.search(r"Experience[:\s]*(\d+[\s\w]*)", text, re.IGNORECASE)
    experience = experience.group(1).strip() if experience else "Not Found"

    current_ctc = re.search(r"Current\s*CTC[:\s]*([\d,]+(?:\s?[kK]|\s?[lL]?\s?pa)?)", text, re.IGNORECASE)
    current_ctc = current_ctc.group(1).strip() if current_ctc else "Not Found"

    expected_ctc = re.search(r"Expected\s*CTC[:\s]*([\d,]+(?:\s?[kK]|\s?[lL]?\s?pa)?)", text, re.IGNORECASE)
    expected_ctc = expected_ctc.group(1).strip() if expected_ctc else "Not Found"

    return {
        "name": name.group() if name else "Unknown",
        "email": email.group() if email else "Not Found",
        "phone": phone.group() if phone else "Not Found",
        "skills": found_skills,
        "education": education if education else ["Not Found"],
        "applied_for": applied_for,
        "experience": experience,
        "current_ctc": current_ctc,
        "expected_ctc": expected_ctc
    }

def extract_resume_data_from_files(request):
    if request.method == 'POST' and request.FILES.getlist('resume'):
        files = request.FILES.getlist('resume')
        extracted_data_list = []

        for file in files:
            try:
                # We won't save the file here; just extract the data
                if file.name.endswith('.pdf'):
                    text = extract_text_from_pdf(file)
                elif file.name.endswith('.docx'):
                    text = extract_text_from_docx(file)
                else:
                    continue  # Skip unsupported file formats

                extracted_data = extract_resume_data(text)
                extracted_data_list.append({
                    "name": extracted_data.get("name", ""),
                    "email": extracted_data.get("email", ""),
                    "phone": extracted_data.get("phone", ""),
                    "skills": extracted_data['skills'],
                    "education": extracted_data['education'],
                    "applied_for": extracted_data['applied_for'],
                    "experience": extracted_data['experience'],
                    "current_ctc": extracted_data['current_ctc'],
                    "expected_ctc": extracted_data['expected_ctc']
                })

            except Exception as e:
                print(f"An error occurred: {e}")

        return JsonResponse(extracted_data_list, safe=False)

    return JsonResponse({"error": "Invalid request"}, status=400)



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
    uploaded_files = []
    all_resumes = []

    if request.method == 'POST' and request.FILES.getlist('resume'):  # Using getlist to retrieve all uploaded files
        resumes = request.FILES.getlist('resume')  # Get all the files from the form

        for resume in resumes:
            try:
                # Save the file using the utility function
                filename, uploaded_file_url = save_uploaded_file(resume)

                # Additional form fields
                experience = request.POST.get(f'experience_{len(uploaded_files)}', None)
                ai_score = round(random.uniform(0, 100), 2)  # Placeholder AI score
                skills = [request.POST.get(f'skills_{len(uploaded_files)}')]
                education = request.POST.get(f'education_{len(uploaded_files)}', '')

                # Save resume data into the database (including filename and other form data)
                Resume.objects.create(
                    name=request.POST.get(f'name_{len(uploaded_files)}', ''),
                    email=request.POST.get(f'email_{len(uploaded_files)}', ''),
                    phone=request.POST.get(f'phone_{len(uploaded_files)}', ''),
                    skills=skills,
                    education=education,
                    experience=float(experience) if experience else None,
                    applied_for=request.POST.get(f'applied_for_{len(uploaded_files)}', 'Unknown'),
                    recruiter_feedback=request.POST.get(f'recruiter_feedback_{len(uploaded_files)}', ''),
                    hiring_status=request.POST.get(f'hiring_status_{len(uploaded_files)}', 'Pending'),
                    score=ai_score,  # AI score as placeholder
                    resume_file=filename
                )

                uploaded_files.append(filename)  # Keep track of successfully uploaded files

            except Exception as e:
                print(f"An error occurred: {e}")

        # Set appropriate upload message based on the number of successfully uploaded files
        if uploaded_files:
            upload_message = f'{len(uploaded_files)} resume(s) uploaded successfully!'
            all_resumes = Resume.objects.filter(resume_file__in=uploaded_files)
            upload_btn_text = "Upload another resume"
        else:
            upload_message = "No resumes were uploaded."
            upload_btn_text = "Upload"
            all_resumes = []



    return render(request, 'resume_screening/upload_page.html', {
        'upload_message': upload_message,
        'upload_btn_text': upload_btn_text,
        'all_resumes': all_resumes
    })