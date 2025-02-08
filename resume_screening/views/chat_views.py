from django.http import JsonResponse
from django.shortcuts import render
import json
import spacy
from textblob import TextBlob
from django.views.decorators.csrf import csrf_exempt
from transformers import pipeline
from django.db.models import Q
from resume_screening.models import Resume
from sentence_transformers import SentenceTransformer, util
import re

nlp = spacy.load("en_core_web_sm")
sentence_model = SentenceTransformer('paraphrase-MiniLM-L6-v2')
model_name = "microsoft/DialoGPT-medium"

# Create a pipeline for text generation using the DialoGPT model
chatbot = pipeline("text-generation", model=model_name, tokenizer=model_name)

PREDEFINED_SKILLS = [
    "python", "java", "javascript", "django", "react", "flask",
    "sql", "html", "css", "aws", "azure", "machine learning",
    "deep learning", "data science", "c++", "git", "linux", "docker", "c#", ".net", "dotnet", "ai", "ml"
]

def chat_assistant(request):
    return render(request, 'resume_screening/chat_assistant.html')

# It extracts entities using spaCy
def extract_entities(text):
    doc = nlp(text)
    entities = {
        'experience': None,
        'skills': [],
        'education': None
    }

    # It handles experience using regex (for eg. "5 years", "5+ years", "more than 5 years")
    experience_pattern = re.compile(r"(more than|over|under|approximately)?\s*(\d+)\s*(years|yr|yrs)?", re.IGNORECASE)
    experience_match = experience_pattern.search(text)

    if experience_match:
        # Extract experience count
        experience_value = int(experience_match.group(2))
        entities['experience'] = experience_value

    # extracting entities using spaCy here
    for ent in doc.ents:
        if ent.label_ == "ORG":
            entities['education'] = ent.text

    text_cleaned = re.sub(r'[^\w\s]', '', text.lower())

    found_skills = set()
    for skill in PREDEFINED_SKILLS:
        skill_normalized = skill.lower().strip()

        if skill_normalized in text_cleaned.split():
            found_skills.add(skill)

    entities['skills'] = list(found_skills)

    return entities


import string


def correct_grammar(query):
    words = query.split()

    # Removing punctuations from the word before correcting them
    words_no_punctuation = [word.strip(string.punctuation) for word in words]

    # Correct grammar for words that are not in the non_correctable_terms list
    corrected_words = [
        str(TextBlob(word).correct()) if word.lower() not in PREDEFINED_SKILLS else word
        for word in words_no_punctuation
    ]

    # reattaching the punctuation to the fixed words
    corrected_query = " ".join([f"{word}{words[i][-1] if words[i][-1] in string.punctuation else ''}"
                                for i, word in enumerate(corrected_words)])

    return corrected_query


def classify_intent(query):
    candidate_labels = ["skills", "experience", "education", "top candidates", "combined search"]
    intent_classifier = pipeline("zero-shot-classification", model="distilbert-base-uncased")
    result = intent_classifier(query, candidate_labels)

    if any(skill in query.lower() for skill in PREDEFINED_SKILLS):
        if "experience" not in query.lower():
            return "skills"
        else:
            return "combined search"

    if "experience" in query.lower() and not any(skill in query.lower() for skill in PREDEFINED_SKILLS):
        return "experience"

    return result['labels'][0]


# Function to perform semantic search using Sentence-BERT
def semantic_search(query, resume_list):
    query_embedding = sentence_model.encode(query, convert_to_tensor=True)

    resume_embeddings = [sentence_model.encode(resume.skills, convert_to_tensor=True) for resume in resume_list]

    similarities = util.pytorch_cos_sim(query_embedding, resume_embeddings)[0]

    sorted_idx = similarities.argsort(descending=True)

    return [resume_list[i] for i in sorted_idx]


def process_query(query):
    # corrects grammar in case user makes type of grammatical mistakes
    corrected_query = correct_grammar(query)

    query = corrected_query.lower()

    # Getting classification to know which area the query is in like experience, skills etc
    intent = classify_intent(query)

    # Getting entities like experience, skills value etc
    entities = extract_entities(query)

    if intent in ["skills", "experience", "combined search"]:
        resumes = None

        # Handle combined search (both skills + experience)
        if intent == "combined search" and entities['experience'] and entities['skills']:
            resumes = Resume.objects.filter(
                experience__gte=entities['experience']
            ).exclude(experience__isnull=True).filter(
                Q(skills__contains=entities['skills'])
            )
        elif intent == "combined search" and entities['experience'] is None:
            resumes = Resume.objects.filter(Q(skills__contains=entities['skills']))
        elif intent == "experience" and entities['experience']:
            resumes = Resume.objects.filter(experience__gte=entities['experience']).exclude(experience__isnull=True)
        elif intent == "skills" and entities['skills']:
            resumes = Resume.objects.filter(Q(skills__contains=entities['skills']))
        elif intent == "education" and entities['education']:
            resumes = Resume.objects.filter(education__icontains=entities['education'])
        elif intent == "top candidates":
            resumes = Resume.objects.all().order_by('-experience')[:5]

        if not resumes and (intent == "skills" or intent == "experience"):
            resume_list = Resume.objects.all()
            resume_list = semantic_search(query, resume_list)
            return resume_list

        return resumes
    return None



def chatbot_query(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            query = data.get('query', '')

            matching_resumes = process_query(query)


            if not matching_resumes:
                conversation = chatbot(query, max_length=100, num_return_sequences=1)
                response = conversation[0]['generated_text']
            else:
                resume_list = []
                for resume in matching_resumes:
                    resume_data = {
                        'id': str(resume.resume_id),
                        'name': resume.name,
                        'email': resume.email,
                        'skills': resume.skills,
                        'experience': resume.experience
                    }
                    resume_list.append(resume_data)

                response = {
                    'response': f"Found {len(matching_resumes)} matching resumes.",
                    'resumes': resume_list
                }

            return JsonResponse(response)

        except Exception as e:
            print(f"Error processing query: {e}")
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request"}, status=400)




@csrf_exempt
def chatbot_response(request):
    if request.method == "POST":
        user_input = request.POST.get('user_input')

        if not user_input:
            return JsonResponse({'error': 'No input provided'}, status=400)

        intent = classify_intent(user_input)

        entities = extract_entities(user_input)

        if intent == "skills":
            resumes = Resume.objects.all()
            relevant_resumes = [resume for resume in resumes if
                                any(skill.lower() in user_input.lower() for skill in resume.skills)]
            response = f"Found {len(relevant_resumes)} resumes with relevant skills."
            if relevant_resumes:
                response += f" Here are some candidates: {', '.join([resume.name for resume in relevant_resumes[:5]])}."
            return JsonResponse({'response': response})

        if intent == "experience":
            resumes = Resume.objects.filter(experience__gte=5)  # Example filter for 5+ years of experience
            response = f"Found {len(resumes)} candidates with 5 or more years of experience."
            return JsonResponse({'response': response})

        conversation = chatbot(user_input)
        response = conversation[0]['generated_text']

        return JsonResponse({'response': response})

    return JsonResponse({'error': 'Invalid request method'}, status=400)
