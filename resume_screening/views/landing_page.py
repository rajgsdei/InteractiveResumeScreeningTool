from django.shortcuts import render
from django.http import JsonResponse
from django.db.models import Avg, Count  # Add Count import here
from collections import Counter
from resume_screening.models import Resume




def home(request):
    return render(request, 'resume_screening/home.html')



def dashboard_data(request):
    # Get basic statistics for the dashboard
    total_resumes = Resume.objects.count()
    shortlisted = Resume.objects.filter(hiring_status="Hired").count()
    rejected = Resume.objects.filter(hiring_status="Rejected").count()
    pending = Resume.objects.filter(hiring_status="Pending").count()

    # Get average scores of resumes
    average_score = Resume.objects.aggregate(Avg('score'))['score__avg']

    # Data for bar chart (hiring status)
    hiring_status_data = {
        "Hired": shortlisted,
        "Rejected": rejected,
        "Pending": pending
    }

    # Fetch the experience and score data for charts
    experience_data = Resume.objects.values('experience').annotate(count=Count('experience')).order_by('experience')
    experience_labels = [str(e['experience']) for e in experience_data]
    experience_values = [e['count'] for e in experience_data]

    score_data = Resume.objects.values('score').annotate(count=Count('score')).order_by('score')
    score_labels = [str(s['score']) for s in score_data]
    score_values = [s['count'] for s in score_data]

    # Get skills distribution (top 10 most common skills)
    all_skills = [skill for resume in Resume.objects.all() for skill in resume.skills]
    skill_counter = Counter(all_skills)
    top_skills = skill_counter.most_common(10)
    skill_labels = [skill[0] for skill in top_skills]
    skill_values = [skill[1] for skill in top_skills]

    # Return data as JSON
    return JsonResponse({
        'total_resumes': total_resumes,
        'hiring_status_data': hiring_status_data,
        'average_score': average_score,
        'experience_labels': experience_labels,
        'experience_values': experience_values,
        'score_labels': score_labels,
        'score_values': score_values,
        'skill_labels': skill_labels,
        'skill_values': skill_values,
    })