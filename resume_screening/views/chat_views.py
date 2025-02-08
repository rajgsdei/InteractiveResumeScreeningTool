from django.http import JsonResponse
from django.shortcuts import render
import json
import spacy
from django.views.decorators.csrf import csrf_exempt
from transformers import pipeline
from django.db.models import Q
from resume_screening.models import Resume
from sentence_transformers import SentenceTransformer, util

# Load spaCy model and transformer models
nlp = spacy.load("en_core_web_sm")
sentence_model = SentenceTransformer('paraphrase-MiniLM-L6-v2')
model_name = "microsoft/DialoGPT-medium"

# Create a pipeline for text generation using the DialoGPT model
chatbot = pipeline("text-generation", model=model_name, tokenizer=model_name)

def chat_assistant(request):
    return render(request, 'resume_screening/chat_assistant.html')

# Function to extract entities using spaCy
def extract_entities(text):
    doc = nlp(text)
    entities = {
        'experience': None,
        'skills': [],
        'education': None
    }

    for ent in doc.ents:
        if ent.label_ == "CARDINAL":  # Experience in years
            entities['experience'] = int(ent.text)
        elif ent.label_ == "ORG":  # Could be used for institutions or skills
            entities['education'] = ent.text
        elif ent.label_ == "SKILL":  # For skills (this could be customized)
            entities['skills'].append(ent.text)

    return entities

# Function to classify intents based on user input
def classify_intent(query):
    candidate_labels = ["skills", "experience", "education", "top candidates"]
    intent_classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")
    result = intent_classifier(query, candidate_labels)
    return result['labels'][0]  # Choose the label with highest score

# Function to perform semantic search using Sentence-BERT
def semantic_search(query, resume_list):
    query_embedding = sentence_model.encode(query, convert_to_tensor=True)
    resume_embeddings = [sentence_model.encode(resume.skills, convert_to_tensor=True) for resume in resume_list]

    similarities = util.pytorch_cos_sim(query_embedding, resume_embeddings)[0]
    sorted_idx = similarities.argsort(descending=True)
    return [resume_list[i] for i in sorted_idx]

# Process the user query and return matching resumes
def process_query(query):
    query = query.lower()

    # Intent classification
    intent = classify_intent(query)

    # Entity extraction for dynamic search
    entities = extract_entities(query)

    # Handle intent-based queries
    if intent == "experience":
        if entities['experience']:
            resumes = Resume.objects.filter(experience__gte=entities['experience'])
            return resumes
    elif intent == "skills":
        if entities['skills']:
            resumes = Resume.objects.filter(
                Q(skills__contains=entities['skills'])
            )
            return resumes
    elif intent == "education":
        if entities['education']:
            resumes = Resume.objects.filter(education__icontains=entities['education'])
            return resumes
    elif intent == "top candidates":
        resumes = Resume.objects.all().order_by('-experience')[:5]  # top 5 candidates based on experience
        return resumes

    return None  # Default fallback

def chatbot_query(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            query = data.get('query', '')

            # Process the query to search for matching resumes (using NLP)
            matching_resumes = process_query(query)

            # Handle conversational response
            if not matching_resumes:
                # Generate a response using the chatbot (DialoGPT)
                conversation = chatbot(query, max_length=100, num_return_sequences=1)
                response = conversation[0]['generated_text']
            else:
                # If we find resumes based on query, display them
                resume_list = []
                for resume in matching_resumes:
                    resume_data = {
                        'id': str(resume.resume_id),
                        'name': resume.name,
                        'email': resume.email,
                        'skills': resume.skills,
                        'experience': resume.experience,
                        'education': resume.education,
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

        # Intent classification
        intent = classify_intent(user_input)

        # Entity extraction
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

        # Use transformer model for more natural conversation responses
        conversation = chatbot(user_input)
        response = conversation[0]['generated_text']

        return JsonResponse({'response': response})

    return JsonResponse({'error': 'Invalid request method'}, status=400)
