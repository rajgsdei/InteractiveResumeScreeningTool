# Interactive Resume Screening

## Introduction
**Interactive Resume Screening** is a web application designed to facilitate the process of screening resumes for recruitment purposes. 
Built using **Django** as the backend framework, the system integrates **MongoDB** for data storage and uses various libraries and tools for natural language processing (NLP), machine learning, and document processing. The app provides features like resume upload, extraction of key information, an interactive dashboard with charts, a resume viewer with pagination, and a Chat Assistant with NLP filters and grammar correction.

## System Description

### Features:
#### 1. Home Page:

The home page has various types of charts on the page based on candidate's profile, including:
- Total number of resumes.
- Resume distribution by hiring status (Hired, Rejected, Pending).
- Average scores of resumes.
- Distribution of experience levels and skills.

#### 2. Upload Resume Page:

- Users can upload resumes (PDF or DOCX files). The system extracts basic details from the resumes, such as name, email, phone number, skills, education, and experience, and pre-fills these details in the upload form before the resume is saved to the database.
- The uploaded resumes are displayed with basic information, and users can click to upload another resume.
- Before saving the resume (s) user can edit fields if needed.

#### 3. View Resume Page:

- This feature allows users to view a list of all uploaded resumes with pagination for easier navigation. Each resume can also be downloaded.

#### 4. About Page:

- Provides information about the project, including its goals, technologies used, and instructions on how to get started.

#### 5. Chat Assistant:

And finally the Chat assistant which is the core and growing feature of the application. Currently it has features like:

- An AI-driven chat assistant that can interact with users by processing their queries.
- Uses NLP for intent classification (skills, experience, education, etc.) and can correct grammatical errors in the queries.
- Offers the ability to filter resumes based on skills, experience, or education, and allows semantic search to find resumes based on content similarity.

### Technologies Used:
- **Backend Framework:** Django
- **Database:** MongoDB (using Djongo for compatibility)
- **NLP and Machine Learning Libraries:** spaCy, TextBlob, Hugging Face Transformers, Sentence-Transformers, and others.
- **Frontend:** HTML, CSS (for templating in Django)
- **Document Processing:** pdfplumber, python-docx
- **Others:** Pypdfium2, PyYAML, and various supporting libraries for tasks like file handling and data visualization.


### Installation and Setup: 
Follow these steps to set up and run the **Interactive Resume Screening** project on your local machine:

#### Prerequisites:
- Python 3.x
- MongoDB (Running locally or using a cloud service)
- pip (Python package manager)


> [!NOTE]
> There is a DB file for SQLite but it is not needed for this project and its dependacies can be ignored.

#### Steps:
1. **Clone the Repository:**
   
   ```
   git clone https://github.com/yourusername/interactive-resume-screening.git
   cd interactive-resume-screening
   ```
3. **Create a Virtual Environment:**
   
   ```
   python -m venv venv
   venv\Scripts\activate
   ```
4. **Install Dependencies:**
   
   ```
   pip install -r requirements.txt
   ```
5. **Configure MongoDB:**
   
   - Ensure that MongoDB is installed and running on your local machine or use a MongoDB cloud instance.
   - In the project, MongoDB is integrated using Djongo, so you don't need to configure a separate connection string.

5. **Run Migrations:**
   
   ```
   python manage.py migrate
   ```
7. **Create a Superuser (Optional):**
   
   ```
   python manage.py createsuperuser
   ```
8. **Create a Superuser (Optional):**
   
   ```
   python manage.py runserver
   ```
9. **Create a Superuser (Optional):**
   
   ```
   python manage.py runserver
   ```
10. **Run the Server:**
    
   ```
   python manage.py runserver
   http://127.0.0.1:8000/
   ```
